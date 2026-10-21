"""Gerador de submissões e consistência física em políticas e agências variadas."""
import json
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from kickoff import dados, medicao, motor, tempo, validar  # noqa: E402
from scripts import buscar  # noqa: E402


class BuscaLocal(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cenarios = {nome: dados.carregar(RAIZ / "dados", nome)
                        for nome in ("Bangkok", "Istanbul", "Hanoi")}

    def test_gerador_e_reproduzivel_e_so_produz_validas(self):
        for nome, cenario in self.cenarios.items():
            with self.subTest(agencia=nome):
                a = list(buscar.gerar_candidatos(cenario, 36, seed=7))
                b = list(buscar.gerar_candidatos(cenario, 36, seed=7))
                self.assertEqual(a, b)
                self.assertEqual(len(a), 36)
                self.assertEqual(len({json.dumps(s, sort_keys=True) for s in a}), 36)
                self.assertGreater(len({json.dumps(s["politica"], sort_keys=True) for s in a}), 1)
                for sub in a:
                    self.assertEqual(validar.validar(sub, cenario), [])
                    self.assertEqual(buscar.para_envio(validar.normalizar(sub, cenario)), sub)

    def test_base_conta_no_limite_e_ranking_e_reproduzivel(self):
        cenario = self.cenarios["Bangkok"]
        base = json.loads((RAIZ / "exemplo_submissao.json").read_text(encoding="utf-8"))
        candidatas = list(buscar.gerar_candidatos(cenario, 3, base=base))
        self.assertEqual(len(candidatas), 3)
        self.assertEqual(candidatas[0], buscar.para_envio(validar.normalizar(base, cenario)))
        relatorio = buscar.buscar(cenario, 3, base=base)
        self.assertEqual(relatorio["avaliadas"], 3)
        self.assertEqual(relatorio["resultados"], sorted(relatorio["resultados"], key=buscar.chave_ranking))
        self.assertTrue(all(not r["violacoes"] for r in relatorio["resultados"]))
        self.assertTrue(relatorio["fronteira_indices"])

    def test_fronteira_preserva_trocas_e_descarta_dominada(self):
        def item(certos, perdidos, demanda, ponta, carregadores, pico=100):
            return {"metricas": {"certos": certos, "upgrades": 0,
                                 "nao_atendidos": perdidos,
                                 "demanda_contratada_kw": demanda,
                                 "energia_ponta_kwh": ponta,
                                 "pico_kw": pico, "energia_kwh": pico},
                    "infraestrutura": {"entrada_kw_util": 40.5,
                                       "carregadores": carregadores,
                                       "potencia_instalada_kw": 7 * carregadores},
                    "violacoes": []}
        resultados = [item(10, 0, 0, 5, 2), item(10, 0, 0, 5, 3, pico=1),
                      item(9, 1, 0, 5, 1), item(10, 0, 10, 0, 2)]
        self.assertEqual(buscar.fronteira_indices(resultados), [0, 2, 3])

    def test_cenarios_alternativos_respeitam_contratos_e_limites(self):
        casos = (
            ("Bangkok", {"dc_60x2": 2, "ac_11": 2}, "a4_150", 80,
             {"prioridade": "proxima_retirada", "divisao": "prioridade", "evitar_ponta": True}),
            ("Istanbul", {"dc_30": 2, "ac_22x2": 1}, "b3_45", None,
             {"prioridade": "chegada", "divisao": "igual", "evitar_ponta": False}),
            ("Hanoi", {"dc_60x2": 2, "ac_11": 2}, "a4_225", 100,
             {"prioridade": "menor_soc", "divisao": "prioridade", "evitar_ponta": True}),
            ("Vienna", {"ac_7": 4}, "a4_150", 30,
             {"prioridade": "proxima_retirada", "divisao": "igual", "evitar_ponta": True}),
        )
        for nome, carregadores, entrada, demanda, politica in casos:
            with self.subTest(agencia=nome):
                cenario = (self.cenarios[nome] if nome in self.cenarios
                           else dados.carregar(RAIZ / "dados", nome))
                sub = {"agencia": nome, "carregadores": carregadores, "entrada": entrada,
                       "politica": politica}
                if demanda is not None:
                    sub["demanda_contratada_kw"] = demanda
                self.assertEqual(validar.validar(sub, cenario), [])
                normalizada = validar.normalizar(sub, cenario)
                resultado = motor.simular(cenario, normalizada)
                ini, fim = tempo.JANELA_PUBLICA
                m = medicao.metricas(resultado.retiradas, resultado.nao_atendidos,
                                     resultado.bins, ini, fim)
                series = medicao.series(resultado.bins, resultado.trace, resultado.retiradas,
                                        resultado.nao_atendidos, ini, fim)
                self.assertEqual(resultado.violacoes, [])
                self.assertEqual(m["contratos"], len(cenario.contratos))
                self.assertEqual(m["certos"] + m["upgrades"] + m["nao_atendidos"], m["contratos"])
                self.assertLessEqual(m["pico_kw"], validar.limite_kw(normalizada, cenario) + 1e-6)
                self.assertLessEqual(max(series["plugados_max"]), cenario.agencia.vagas)
                if politica["evitar_ponta"]:
                    self.assertAlmostEqual(m["energia_ponta_kwh"], 0.0, places=6)


if __name__ == "__main__":
    unittest.main()
