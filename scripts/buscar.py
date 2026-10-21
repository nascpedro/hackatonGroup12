"""Busca local, limitada e reproduzível, de submissões válidas.

Uso: python3 scripts/buscar.py Bangkok --max-avaliacoes 24 --saida resultados/bangkok.json
Não lê .env, não importa kickoff.api e não faz requisições de rede.
"""
import argparse
import itertools
import json
import random
import sys
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from kickoff import dados, medicao, motor, tempo, validar  # noqa: E402


def planos_carregadores(cenario):
    """Todos os conjuntos de equipamentos com ao menos uma saída e dentro das vagas."""
    ids = sorted(cenario.carregadores)
    for n in range(1, cenario.agencia.vagas + 1):
        for grupo in itertools.combinations_with_replacement(ids, n):
            if sum(cenario.carregadores[k].saidas for k in grupo) <= cenario.agencia.vagas:
                yield {k: grupo.count(k) for k in sorted(set(grupo))}


def entradas_validas(cenario):
    existente = cenario.entradas[cenario.agencia.entrada_existente]
    return [e for e in sorted(cenario.entradas.values(), key=lambda e: (e.kw_util, e.id))
            if e.id == existente.id or (e.kva >= validar.B3_KVA and e.kw_util >= existente.kw_util)]


def para_envio(normalizada):
    """Retira o campo interno de demanda B3, proibido na submissão à API."""
    sub = dict(normalizada)
    if sub["demanda_contratada_kw"] is None:
        del sub["demanda_contratada_kw"]
    return sub


def gerar_candidatos(cenario, quantidade, seed=12, base=None):
    """Inclui uma base opcional e amostra equipamentos, entradas e políticas."""
    if quantidade < 1:
        raise ValueError("quantidade deve ser positiva")
    rng = random.Random(seed)
    planos = list(planos_carregadores(cenario))
    rng.shuffle(planos)
    entradas = entradas_validas(cenario)
    politicas = [dict(zip(validar.MENU, valores))
                 for valores in itertools.product(*(validar.MENU[k] for k in validar.MENU))]
    rng.shuffle(politicas)
    vistos = set()
    produzidos = 0

    if base is not None:
        erros = validar.validar(base, cenario)
        if erros:
            raise ValueError(f"submissão base inválida: {erros}")
        normalizada = validar.normalizar(base, cenario)
        vistos.add(json.dumps(normalizada, sort_keys=True))
        yield para_envio(normalizada)
        produzidos += 1

    tentativas = 0
    while produzidos < quantidade and tentativas < quantidade * 50:
        i = tentativas
        plano = planos[i % len(planos)]
        ent = entradas[rng.randrange(len(entradas))]
        sub = {"agencia": cenario.agencia.nome, "carregadores": plano,
               "entrada": ent.id, "politica": politicas[i % len(politicas)]}
        if ent.kva > validar.B3_KVA:
            teto = validar.teto_demanda(ent)
            meio = max(validar.DEMANDA_MIN_KW, (teto // 20) * 10)
            sub["demanda_contratada_kw"] = rng.choice((validar.DEMANDA_MIN_KW, meio, teto))
        erros = validar.validar(sub, cenario)
        if erros:
            raise AssertionError(f"gerador produziu submissão inválida: {erros}")
        normalizada = validar.normalizar(sub, cenario)
        chave = json.dumps(normalizada, sort_keys=True)
        if chave not in vistos:
            vistos.add(chave)
            yield para_envio(normalizada)
            produzidos += 1
        tentativas += 1


def avaliar(cenario, sub):
    erros = validar.validar(sub, cenario)
    if erros:
        raise ValueError(f"submissão inválida: {erros}")
    normalizada = validar.normalizar(sub, cenario)
    resultado = motor.simular(cenario, normalizada)
    ini, fim = tempo.JANELA_PUBLICA
    metricas = medicao.metricas(resultado.retiradas, resultado.nao_atendidos,
                                resultado.bins, ini, fim)
    metricas["demanda_contratada_kw"] = normalizada["demanda_contratada_kw"] or 0.0
    infraestrutura = {
        "entrada_kw_util": cenario.entradas[sub["entrada"]].kw_util,
        "carregadores": sum(sub["carregadores"].values()),
        "saidas": sum(cenario.carregadores[k].saidas * n for k, n in sub["carregadores"].items()),
        "potencia_instalada_kw": sum(cenario.carregadores[k].potencia_kw * n
                                     for k, n in sub["carregadores"].items()),
    }
    return {"submissao": sub, "metricas": metricas, "infraestrutura": infraestrutura,
            "violacoes": resultado.violacoes}


def chave_ranking(item):
    """Heurística provisória; não representa a nota do juiz."""
    m = item["metricas"]
    infra = item["infraestrutura"]
    return (len(item["violacoes"]) > 0, -m["certos"] - m["upgrades"],
            -m["certos"], infra["entrada_kw_util"], infra["carregadores"],
            infra["potencia_instalada_kw"], m["pico_kw"], m["energia_ponta_kwh"])


def buscar(cenario, quantidade, seed=12, base=None):
    resultados = [avaliar(cenario, sub) for sub in gerar_candidatos(cenario, quantidade, seed, base)]
    resultados.sort(key=chave_ranking)
    return {"agencia": cenario.agencia.nome, "periodo": "publico",
            "criterio": "atendimento, categoria exata, infraestrutura aproximada, pico, energia de ponta; sem custos ou pesos oficiais",
            "avaliadas": len(resultados), "seed": seed, "resultados": resultados}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("agencia")
    ap.add_argument("--max-avaliacoes", type=int, default=24)
    ap.add_argument("--seed", type=int, default=12)
    ap.add_argument("--base", type=Path, help="submissão válida para incluir na busca")
    ap.add_argument("--dados", type=Path, default=RAIZ / "dados")
    ap.add_argument("--saida", type=Path, help="salva todas as avaliações em JSON")
    a = ap.parse_args(argv)
    if a.max_avaliacoes < 1:
        ap.error("--max-avaliacoes deve ser positivo")
    cenario = dados.carregar(a.dados, a.agencia)
    base = json.loads(a.base.read_text(encoding="utf-8-sig")) if a.base else None
    relatorio = buscar(cenario, a.max_avaliacoes, a.seed, base)
    if a.saida:
        a.saida.parent.mkdir(parents=True, exist_ok=True)
        a.saida.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        candidatas = a.saida.with_name(a.saida.stem + "_top5.json")
        candidatas.write_text(json.dumps([r["submissao"] for r in relatorio["resultados"][:5]],
                                         ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(f"{a.agencia}: {relatorio['avaliadas']} configurações válidas simuladas (sem API)")
    for i, item in enumerate(relatorio["resultados"][:5], 1):
        m = item["metricas"]
        print(f"{i}. atendidos={m['certos'] + m['upgrades']}/{m['contratos']} "
              f"certos={m['certos']} pico={m['pico_kw']:.2f} kW "
              f"violações={len(item['violacoes'])} "
              f"sub={json.dumps(item['submissao'], ensure_ascii=False, sort_keys=True)}")
    if a.saida:
        print(f"Resultados completos: {a.saida}")
        print(f"Cinco submissões para simular localmente: {candidatas}")


if __name__ == "__main__":
    main()
