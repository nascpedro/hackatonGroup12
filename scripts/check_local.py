"""Verificação reproduzível e offline do kit e da referência gratuita de Bangkok.

Uso: python3 scripts/check_local.py [--strict]
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


def conferir_numero(nome, meu, juiz):
    tolerancia = 1e-6
    if abs(meu - juiz) > tolerancia:
        raise AssertionError(f"{nome}: local={meu}, juiz={juiz}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="exige igualdade também na série fila_max")
    args = parser.parse_args()
    if sys.version_info < (3, 10):
        raise SystemExit("Python 3.10+ é necessário")

    for nome in ("Bangkok", "Hanoi", "Istanbul"):
        if not (KIT / "dados" / nome).is_dir():
            raise SystemExit(f"dados ausentes: dados/{nome}")
    if not FIXTURE.is_file():
        raise SystemExit(f"referência oficial ausente: {FIXTURE}")

    print("1/3 Testes unitários locais", flush=True)
    subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "testes"],
                   cwd=KIT, check=True)

    sys.path.insert(0, str(KIT))
    from kickoff import dados, medicao, motor, tempo, validar

    print("2/3 Simulação de Bangkok", flush=True)
    sub = json.loads((KIT / "exemplo_submissao.json").read_text(encoding="utf-8"))
    juiz = json.loads(FIXTURE.read_text(encoding="utf-8"))
    cen = dados.carregar(KIT / "dados", "Bangkok")
    erros = validar.validar(sub, cen)
    if erros:
        raise AssertionError(f"submissão de exemplo inválida: {erros}")
    normalizada = validar.normalizar(sub, cen)
    resultado = motor.simular(cen, normalizada)
    if resultado.violacoes:
        raise AssertionError(f"violações locais: {resultado.violacoes[:3]}")
    ini, fim = tempo.JANELA_PUBLICA
    metricas = medicao.metricas(resultado.retiradas, resultado.nao_atendidos,
                                resultado.bins, ini, fim)
    serie = medicao.series(resultado.bins, resultado.trace, resultado.retiradas,
                           resultado.nao_atendidos, ini, fim)

    print("3/3 Comparação com resposta oficial salva (sem API)", flush=True)
    for nome, esperado in juiz["metricas"].items():
        conferir_numero(f"metricas.{nome}", metricas[nome], esperado)
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
        if args.strict:
            raise SystemExit(1)
    else:
        print("OK: fila_max também coincide")


if __name__ == "__main__":
    main()
