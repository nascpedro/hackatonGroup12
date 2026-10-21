"""Reclassifica avaliações salvas usando custos e pesos oficiais de H4.

Uso: python3 scripts/reclassificar.py resultados/hanoi.json --catalogo dados/catalogo.json
Não ressimula, não lê .env e não chama a API. Atualize o catálogo antes de usar.
"""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from kickoff import dados, nota, validar  # noqa: E402


def _numero(valor):
    return isinstance(valor, (int, float)) and not isinstance(valor, bool) and math.isfinite(valor)


def reclassificar(relatorio, catalogo, dados_dir=RAIZ / "dados", catalogo_sha256=None):
    """Calcula a nota das métricas públicas já salvas; falha se H4 estiver incompleto."""
    agencia = relatorio["agencia"]
    pesos = catalogo.get("pesos", {}).get(agencia)
    nomes_pesos = [nome for nome, _ in nota.ITENS]
    if not isinstance(pesos, dict) or any(not _numero(pesos.get(nome)) for nome in nomes_pesos):
        raise ValueError(f"catálogo sem os pesos oficiais completos de {agencia}; atualize dados/catalogo.json após H4")
    cenario = dados.carregar(dados_dir, agencia, catalogo)
    pontuados = []
    for item in relatorio["resultados"]:
        sub = item["submissao"]
        erros = validar.validar(sub, cenario)
        if erros or item.get("violacoes"):
            raise ValueError(f"submissão inválida ou com violações no relatório: {erros or item['violacoes']}")
        normalizada = validar.normalizar(sub, cenario)
        custo = nota.custo_infra(normalizada, cenario)
        if custo is None or not all(_numero(x) for x in custo.values()):
            raise ValueError(f"catálogo sem custo oficial para a infraestrutura de {sub}")
        metricas = dict(item["metricas"])
        demanda = normalizada["demanda_contratada_kw"] or 0.0
        if abs(metricas.get("demanda_contratada_kw", demanda) - demanda) > 1e-8:
            raise ValueError(f"demanda arquivada difere da submissão: {sub}")
        metricas["demanda_contratada_kw"] = demanda
        metricas["custo_infra"] = custo["total"]
        if any(not _numero(metricas.get(chave)) for _, chave in nota.ITENS):
            raise ValueError("relatório sem métricas necessárias à pontuação")
        pontos = nota.pontuar(metricas, pesos)
        pontuados.append({**item, "metricas": metricas, "custo_infra": custo,
                          "pontos": pontos, "nota": pontos["nota"]})
    pontuados.sort(key=lambda r: (-r["nota"], -r["metricas"]["certos"] - r["metricas"]["upgrades"],
                                   r["custo_infra"]["total"],
                                   json.dumps(r["submissao"], sort_keys=True)))
    return {"agencia": agencia, "periodo": relatorio["periodo"],
            "criterio": "nota calculada das metricas locais com custos e pesos do catalogo H4",
            "catalogo_sha256": catalogo_sha256, "avaliadas": len(pontuados),
            "resultados": pontuados}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("relatorio", type=Path, help="JSON gerado por scripts/buscar.py")
    ap.add_argument("--catalogo", type=Path, default=RAIZ / "dados" / "catalogo.json")
    ap.add_argument("--dados", type=Path, default=RAIZ / "dados")
    ap.add_argument("--saida", type=Path, help="padrão: RELATORIO_pontuado.json")
    a = ap.parse_args(argv)
    origem = json.loads(a.relatorio.read_text(encoding="utf-8-sig"))
    catalogo_bytes = a.catalogo.read_bytes()
    catalogo = json.loads(catalogo_bytes.decode("utf-8-sig"))
    try:
        relatorio = reclassificar(origem, catalogo, a.dados, hashlib.sha256(catalogo_bytes).hexdigest())
    except ValueError as erro:
        ap.error(str(erro))
    destino = a.saida or a.relatorio.with_name(a.relatorio.stem + "_pontuado.json")
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    candidatas = destino.with_name(destino.stem + "_top5.json")
    candidatas.write_text(json.dumps([r["submissao"] for r in relatorio["resultados"][:5]],
                                     ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(f"{relatorio['agencia']}: {relatorio['avaliadas']} candidatas reclassificadas, "
          f"melhor nota local={relatorio['resultados'][0]['nota']:.3f}")
    print(f"Relatório: {destino}")
    print(f"Cinco submissões: {candidatas}")


if __name__ == "__main__":
    main()
