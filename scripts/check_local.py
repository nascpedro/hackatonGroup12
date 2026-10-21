"""Verificação reproduzível e offline do kit e da referência gratuita de Bangkok.

Uso: python3 scripts/check_local.py [--strict] [--caso SUB.json RESPOSTA.json]
Nenhuma parte deste script lê .env, importa kickoff.api ou chama a rede.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
KIT = ROOT
FIXTURE = KIT / "testes" / "fixtures" / "bangkok_exemplo_juiz.json"
FILA_SUB = KIT / "testes" / "fixtures" / "bangkok_fila_sub.json"
FILA_FIXTURE = KIT / "testes" / "fixtures" / "bangkok_fila_juiz.json"
IGUAL_SUB = KIT / "testes" / "fixtures" / "bangkok_politicas_igual_sub.json"
IGUAL_FIXTURE = KIT / "testes" / "fixtures" / "bangkok_politicas_igual_juiz.json"


def conferir_numero(nome, meu, juiz):
    tolerancia = 1e-6
    if abs(meu - juiz) > tolerancia:
        raise AssertionError(f"{nome}: local={meu}, juiz={juiz}")


def comparar_caso(sub_path, resposta_path, strict):
    from kickoff import dados, medicao, motor, tempo, validar

    sub = json.loads(sub_path.read_text(encoding="utf-8-sig"))
    juiz = json.loads(resposta_path.read_text(encoding="utf-8-sig"))
    nome = sub["agencia"]
    if juiz.get("agencia") != nome or not juiz.get("valido", False):
        raise AssertionError(f"referência incompatível ou inválida: {resposta_path}")
    cen = dados.carregar(KIT / "dados", nome)
    erros = validar.validar(sub, cen)
    if erros:
        raise AssertionError(f"submissão inválida em {sub_path}: {erros}")
    normalizada = validar.normalizar(sub, cen)
    resultado = motor.simular(cen, normalizada)
    if resultado.violacoes:
        raise AssertionError(f"violações locais: {resultado.violacoes[:3]}")
    ini, fim = tempo.JANELA_PUBLICA
    metricas = medicao.metricas(resultado.retiradas, resultado.nao_atendidos,
                                resultado.bins, ini, fim)
    serie = medicao.series(resultado.bins, resultado.trace, resultado.retiradas,
                           resultado.nao_atendidos, ini, fim)

    for nome, esperado in juiz["metricas"].items():
        conferir_numero(f"metricas.{nome}", metricas[nome], esperado)
    for nome in ("inicio_min", "passo_min"):
        conferir_numero(f"series.{nome}", serie[nome], juiz["series"][nome])
    for nome in ("potencia_kw", "plugados_max", "nao_atendidos_min", "soc_retirada"):
        atual, esperado = serie[nome], juiz["series"][nome]
        if len(atual) != len(esperado):
            raise AssertionError(f"series.{nome}: tamanhos {len(atual)} e {len(esperado)}")
        for indice, (a, b) in enumerate(zip(atual, esperado)):
            conferir_numero(f"series.{nome}[{indice}]", a, b)

    diferencas_fila = sum(a != b for a, b in zip(serie["fila_max"], juiz["series"]["fila_max"]))
    if len(serie["fila_max"]) != len(juiz["series"]["fila_max"]):
        raise AssertionError("series.fila_max: tamanhos diferentes")
    print(f"OK: {metricas['contratos']} contratos; métricas, potência, plugados e retiradas coincidem")
    if diferencas_fila:
        print(f"PENDENTE: fila_max diverge em {diferencas_fila} janelas de 15 min")
        if strict:
            raise SystemExit(1)
    else:
        print("OK: fila_max também coincide")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="exige igualdade também na série fila_max")
    parser.add_argument("--caso", nargs=2, action="append", metavar=("SUB", "RESPOSTA"),
                        type=Path, help="acrescenta comparação com outra resposta oficial já salva")
    args = parser.parse_args()
    if sys.version_info < (3, 10):
        raise SystemExit("Python 3.10+ é necessário")
    for nome in ("Bangkok", "Hanoi", "Istanbul", "Vienna"):
        if not (KIT / "dados" / nome).is_dir():
            raise SystemExit(f"dados ausentes: dados/{nome}")
    for fixture in (FIXTURE, FILA_SUB, FILA_FIXTURE, IGUAL_SUB, IGUAL_FIXTURE):
        if not fixture.is_file():
            raise SystemExit(f"referência oficial ausente: {fixture}")

    print("1/3 Testes unitários locais", flush=True)
    subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "testes"],
                   cwd=KIT, check=True)
    sys.path.insert(0, str(KIT))
    casos = [(KIT / "exemplo_submissao.json", FIXTURE), (FILA_SUB, FILA_FIXTURE),
             (IGUAL_SUB, IGUAL_FIXTURE)]
    casos += [(sub, resposta) for sub, resposta in (args.caso or [])]
    print(f"2/3 Simulação de {len(casos)} caso(s)", flush=True)
    for sub, resposta in casos:
        print(f"3/3 Comparação offline: {sub} × {resposta}", flush=True)
        comparar_caso(sub, resposta, args.strict)


if __name__ == "__main__":
    main()
