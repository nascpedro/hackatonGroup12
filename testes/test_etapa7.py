"""Corte de potência anunciado na H4 de Marrakech (regulamento 11)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from kickoff import dados  # noqa: E402
from kickoff.motor import Motor, Veiculo  # noqa: E402


class Etapa7(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cenario = dados.carregar(Path(__file__).resolve().parents[1] / "dados", "Marrakech")

    def test_corte_reduz_limite_e_o_restaura(self):
        sub = {"carregadores": {"dc_30": 2}, "entrada": "b3_45",
               "demanda_contratada_kw": None,
               "politica": {"prioridade": "chegada", "divisao": "igual", "evitar_ponta": False}}
        m = Motor(self.cenario, sub)
        modelo = self.cenario.modelos["Renault Kwid E-Tech"]
        for i, ponto in enumerate(m.pontos):
            m.plugar(Veiculo(f"carro-{i}", modelo, 1, 20), ponto)
        m.recalcular_potencias(31680)
        self.assertAlmostEqual(sum(v.potencia_kw for p in m.pontos for v in p.conectados), 40.5)

        m.agendar_eventos([["corte", "Marrakech", 31680, 34560, 0.7],
                           ["corte", "Hanoi", 31680, 34560, 0.5]])
        eventos = sorted((t, payload) for t, _, _, tipo, payload in m.heap if tipo == "evento")
        self.assertEqual([(t, p[2]) for t, p in eventos], [(31680, True), (34560, False)])
        m.on_evento(31680, *eventos[0][1])
        self.assertAlmostEqual(m.limite_kw, 28.35)
        self.assertAlmostEqual(sum(v.potencia_kw for p in m.pontos for v in p.conectados), 28.35)
        m.on_evento(34560, *eventos[1][1])
        self.assertAlmostEqual(m.limite_kw, 40.5)
        self.assertAlmostEqual(sum(v.potencia_kw for p in m.pontos for v in p.conectados), 40.5)

    def test_corte_a4_incide_sobre_demanda_contratada(self):
        sub = {"carregadores": {"dc_30": 4}, "entrada": "a4_150",
               "demanda_contratada_kw": 130,
               "politica": {"prioridade": "chegada", "divisao": "igual", "evitar_ponta": False}}
        m = Motor(self.cenario, sub)
        modelo = self.cenario.modelos["Renault Kwid E-Tech"]
        for i, ponto in enumerate(m.pontos):
            m.plugar(Veiculo(f"a4-{i}", modelo, 1, 20), ponto)
        m.recalcular_potencias(31680)
        self.assertAlmostEqual(m.limite_kw, 130)
        self.assertGreater(sum(v.potencia_kw for p in m.pontos for v in p.conectados), 91)

        m.agendar_eventos([["corte", "Marrakech", 31680, 34560, 0.7]])
        eventos = sorted((t, payload) for t, _, _, tipo, payload in m.heap if tipo == "evento")
        m.on_evento(31680, *eventos[0][1])
        self.assertAlmostEqual(m.limite_kw, 91)
        self.assertAlmostEqual(sum(v.potencia_kw for p in m.pontos for v in p.conectados), 91)

        m.on_evento(34560, *eventos[1][1])
        self.assertAlmostEqual(m.limite_kw, 130)
        self.assertGreater(sum(v.potencia_kw for p in m.pontos for v in p.conectados), 91)


if __name__ == "__main__":
    unittest.main()
