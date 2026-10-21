"""Busca e ensaios de continuidade de Zurich, apenas com dados locais e biblioteca padrão.

python3 scripts/analisar_zurich.py busca --saida resultados/zurich_busca_robusta.json
python3 scripts/analisar_zurich.py cenarios --submissoes resultados/zurich_finalistas.json

Os cenários sintéticos não são previsões das semanas ocultas. Não lê .env ou usa API.
"""
import argparse
import concurrent.futures
import hashlib
import itertools
import json
import random
import subprocess
import sys
import tempfile
from collections import Counter
from dataclasses import replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from kickoff import dados, medicao, motor, nota, tempo, validar  # noqa: E402
from scripts.buscar import planos_carregadores  # noqa: E402
from simular import avaliar as avaliar_publico, ler_eventos  # noqa: E402


def gerar_candidatas(cenario):
    """Famílias DC com 3–4 saídas e até 11.500 de obra, mais controles explícitos."""
    planos = [p for p in planos_carregadores(cenario)
              if sum(cenario.carregadores[k].saidas * n for k, n in p.items()) >= 3
              and any(cenario.carregadores[k].tipo == "DC" for k in p)
              and sum(cenario.carregadores[k].custo * n for k, n in p.items()) <= 11500]
    planos += [{"ac_22x2": 2}, {"dc_30": 4}]
    subs = []
    for plano in planos:
        for prioridade, evitar, divisao in itertools.product(
                ("proxima_retirada", "chegada", "menor_soc"), (False, True), ("igual", "prioridade")):
            subs.append({"agencia": "Zurich", "carregadores": plano,
                         "entrada": cenario.agencia.entrada_existente,
                         "politica": {"prioridade": prioridade, "evitar_ponta": evitar, "divisao": divisao}})
    for demanda, divisao in itertools.product((80, 100, 130), ("igual", "prioridade")):
        subs.append({"agencia": "Zurich", "carregadores": {"dc_30": 2, "ac_7": 2},
                     "entrada": "a4_150", "demanda_contratada_kw": demanda,
                     "politica": {"prioridade": "proxima_retirada", "evitar_ponta": False, "divisao": divisao}})
    return subs


def gerar_cenarios(cenario):
    """Mantém a frota desde T0; altera somente contratos copiados para as semanas 5–8."""
    ini, fim = tempo.JANELA_PUBLICA
    periodo = fim - ini
    semana = 7 * tempo.DIA
    copias = [replace(c, id=c.id + ":ciclo2", retirada_t=c.retirada_t + periodo,
                      devolucao_t=None if c.devolucao_t is None else c.devolucao_t + periodo)
              for c in cenario.contratos]
    casos = [{"nome": "publico", "sintetico": False, "cenario": cenario,
              "ini": ini, "fim": fim, "descricao": "Kit público sem alteração."}]

    def incluir(nome, contratos, descricao):
        casos.append({"nome": nome, "sintetico": True,
                      "cenario": replace(cenario, contratos=list(cenario.contratos) + contratos),
                      "ini": fim, "fim": fim + periodo, "descricao": descricao})

    incluir("continuacao", copias, "Repete os contratos públicos nas semanas 5–8, sem reiniciar a frota.")
    for pct in (5, 10):
        selecionados = sorted(random.Random(12).sample(range(len(copias)), len(copias) * pct // 100))
        extras = [replace(copias[i], id=copias[i].id + f":extra{pct}") for i in selecionados]
        incluir(f"demanda_mais_{pct}pct", copias + extras,
                f"Continuação com {len(extras)} reservas adicionais, nos horários de reservas existentes (semente 12).")
    incluir("devolucao_menos_10pct_km",
            [replace(c, km_devolucao=None if c.km_devolucao is None else c.km_devolucao * 0.9) for c in copias],
            "Continuação com 10% menos km de autonomia na devolução; não equivale a 10% mais energia.")
    adiantados = []
    for c in copias:
        abertura, _ = cenario.agencia.horario[tempo.dia_semana(c.retirada_t)]
        inicio_dia = int(c.retirada_t // tempo.DIA) * tempo.DIA
        adiantados.append(replace(c, retirada_t=max(c.retirada_t - 30, inicio_dia + abertura)))
    incluir("retiradas_30min_antes", adiantados,
            "Continuação com retiradas até 30 min antes, respeitando a abertura; devoluções mantidas.")
    destinos = {origem: destino for destino, origem in enumerate((1, 3, 0, 2))}
    reordenados = []
    for c in cenario.contratos:
        origem = int((c.retirada_t - ini) // semana)
        delta = periodo + (destinos[origem] - origem) * semana
        reordenados.append(replace(c, id=c.id + ":reordenado", retirada_t=c.retirada_t + delta,
                                   devolucao_t=None if c.devolucao_t is None else c.devolucao_t + delta))
    incluir("semanas_reordenadas", reordenados,
            "Continuação na ordem das semanas públicas 2, 4, 1, 3; preserva duração e dia da semana.")
    return casos


class MotorObservado(motor.Motor):
    """Acrescenta diagnóstico às retiradas sem alterar as decisões do motor."""
    def __init__(self, cenario, sub, eventos, ini, fim):
        self.ini_observado, self.fim_observado = ini, fim
        self.perdas = []
        self.min_prontos = None
        super().__init__(cenario, sub, eventos)

    def on_retirada(self, contrato_id, t):
        c = self.contratos[contrato_id]
        observar = self.ini_observado <= t < self.fim_observado
        antes = len(self.nao_atendidos)
        if observar:
            prontos = sum(v.soc >= 80 - 1e-8 for v in self.patio.values())
            self.min_prontos = prontos if self.min_prontos is None else min(self.min_prontos, prontos)
        super().on_retirada(contrato_id, t)
        if observar and len(self.nao_atendidos) > antes:
            self.perdas.append({"contrato": contrato_id, "minuto": t, "categoria": c.categoria,
                                "semana": int((t - self.ini_observado) // (7 * tempo.DIA)) + 1,
                                "fila_interna": len(self.fila),
                                "plugados": sum(len(p.conectados) for p in self.pontos),
                                "potencia_kw": sum(v.potencia_kw for p in self.pontos for v in p.conectados)})


def avaliar_cenario(caso, sub, catalogo, eventos):
    c = caso["cenario"]
    erros = validar.validar(sub, c)
    if erros:
        raise ValueError(erros)
    normalizada = validar.normalizar(sub, c)
    m = MotorObservado(c, normalizada, eventos, caso["ini"], caso["fim"])
    res = m.rodar()
    metricas = medicao.metricas(res.retiradas, res.nao_atendidos, res.bins, caso["ini"], caso["fim"])
    custo = nota.custo_infra(normalizada, c)
    metricas.update(demanda_contratada_kw=normalizada["demanda_contratada_kw"] or 0,
                    custo_infra=custo["total"])
    pontos = nota.pontuar(metricas, catalogo["pesos"]["Zurich"])
    return {"submissao": sub, "cenario": caso["nome"], "sintetico": caso["sintetico"],
            "metricas": metricas, "custo_infra": custo, "nota": 0 if res.violacoes else pontos["nota"],
            "pontos": pontos, "violacoes": res.violacoes,
            "diagnostico": {"perdas_por_categoria": dict(Counter(x["categoria"] for x in m.perdas)),
                            "perdas_por_semana": dict(Counter(x["semana"] for x in m.perdas)),
                            "min_prontos_soc80_antes_retirada": m.min_prontos,
                            "perdas": m.perdas}}


def executar_worker(origem, destino):
    job = json.loads(Path(origem).read_text(encoding="utf-8"))
    catalogo = json.loads(Path(job["catalogo"]).read_text(encoding="utf-8"))
    c = dados.carregar(Path(job["dados"]), "Zurich", catalogo)
    eventos = job["eventos"]
    if job["modo"] == "busca":
        cenarios = {"Zurich": c}
        resultados = [{"submissao": s, **avaliar_publico(s, cenarios, Path(job["dados"]), catalogo, eventos, False)}
                      for s in job["itens"]]
    else:
        casos = {x["nome"]: x for x in gerar_cenarios(c)}
        resultados = [avaliar_cenario(casos[item["cenario"]], item["submissao"], catalogo, eventos)
                      for item in job["itens"]]
    Path(destino).write_text(json.dumps(resultados, ensure_ascii=False), encoding="utf-8")


def executar_lotes(itens, a, eventos):
    tamanho = 12 if a.modo == "busca" else 3
    lotes = [itens[i:i + tamanho] for i in range(0, len(itens), tamanho)]
    with tempfile.TemporaryDirectory(prefix="zurich-offline-") as tmp:
        def executar(i):
            origem, destino = Path(tmp) / f"entrada-{i}.json", Path(tmp) / f"saida-{i}.json"
            job = {"modo": a.modo, "catalogo": str(a.catalogo.resolve()), "dados": str(a.dados.resolve()),
                   "eventos": eventos, "itens": lotes[i]}
            origem.write_text(json.dumps(job), encoding="utf-8")
            subprocess.run([sys.executable, str(Path(__file__).resolve()), "--worker", str(origem), str(destino)],
                           check=True, capture_output=True, text=True)
            return i, json.loads(destino.read_text(encoding="utf-8"))
        resultados = [None] * len(lotes)
        feitos = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as pool:
            futuros = [pool.submit(executar, i) for i in range(len(lotes))]
            for futuro in concurrent.futures.as_completed(futuros):
                i, res = futuro.result()
                resultados[i] = res
                feitos += len(res)
                print(f"{a.modo}: {feitos}/{len(itens)} avaliações locais", flush=True)
    return [r for lote in resultados for r in lote]


def resumir_cenarios(resultados):
    grupos = {}
    for r in resultados:
        grupos.setdefault(json.dumps(r["submissao"], sort_keys=True), []).append(r)
    resumo = []
    for grupo in grupos.values():
        sinteticos = [r for r in grupo if r["sintetico"]]
        publico = next(r for r in grupo if not r["sintetico"])
        resumo.append({"submissao": publico["submissao"], "nota_publica": publico["nota"],
                       "menor_nota_sintetica": min(r["nota"] for r in sinteticos),
                       "media_nota_sintetica": sum(r["nota"] for r in sinteticos) / len(sinteticos),
                       "max_perdidos_sinteticos": max(r["metricas"]["nao_atendidos"] for r in sinteticos)})
    return sorted(resumo, key=lambda r: (-r["menor_nota_sintetica"], -r["media_nota_sintetica"]))


def main(argv=None):
    if len(sys.argv) > 1 and sys.argv[1] == "--worker":
        executar_worker(sys.argv[2], sys.argv[3])
        return
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("modo", choices=("busca", "cenarios"))
    ap.add_argument("--submissoes", type=Path, help="lista JSON de finalistas para os cenários")
    ap.add_argument("--dados", type=Path, default=RAIZ / "dados")
    ap.add_argument("--catalogo", type=Path, default=RAIZ / "dados/catalogo.json")
    ap.add_argument("--eventos", type=Path, help="snapshot de eventos; filtra somente Zurich")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--saida", type=Path)
    a = ap.parse_args(argv)
    if a.jobs < 1:
        ap.error("--jobs deve ser positivo")
    if a.modo == "cenarios" and a.submissoes is None:
        ap.error("cenarios exige --submissoes")
    catalogo = json.loads(a.catalogo.read_text(encoding="utf-8-sig"))
    c = dados.carregar(a.dados, "Zurich", catalogo)
    eventos = [e for e in ler_eventos(a.eventos) if len(e) > 1 and e[1] == "Zurich"]
    subs = gerar_candidatas(c) if a.modo == "busca" else json.loads(a.submissoes.read_text(encoding="utf-8-sig"))
    if not isinstance(subs, list) or not subs:
        ap.error("submissoes deve ser uma lista não vazia")
    for sub in subs:
        erros = validar.validar(sub, c)
        if erros:
            ap.error(str(erros))
    casos = gerar_cenarios(c)
    itens = subs if a.modo == "busca" else [{"submissao": s, "cenario": x["nome"]} for s in subs for x in casos]
    resultados = executar_lotes(itens, a, eventos)
    if a.modo == "busca":
        resultados.sort(key=lambda r: (-r["nota"], r["metricas"]["nao_atendidos"], json.dumps(r["submissao"], sort_keys=True)))
    meta = {"agencia": "Zurich", "modo": a.modo, "avaliadas": len(resultados),
            "catalogo_sha256": hashlib.sha256(a.catalogo.read_bytes()).hexdigest(),
            "dados_sha256": {str(p.relative_to(a.dados / "Zurich")): hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in sorted((a.dados / "Zurich").rglob("*")) if p.is_file()},
            "eventos": eventos, "resultados": resultados}
    if a.modo == "cenarios":
        meta["cenarios"] = [{k: v for k, v in x.items() if k != "cenario"} for x in casos]
        meta["ranking_sensibilidade"] = resumir_cenarios(resultados)
        meta["limite"] = "Cenários sintéticos sem probabilidades estimadas; não preveem as semanas ocultas."
    destino = a.saida or RAIZ / "resultados" / f"zurich_{a.modo}_robusta.json"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Resultados offline: {destino}")


if __name__ == "__main__":
    main()
