"""Duas camadas de potência e limite da agência (regulamento 6.3.5)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from kickoff import dados, tempo  # noqa: E402
from kickoff.motor import Motor, Veiculo  # noqa: E402
from kickoff.modelo import Agencia, Cenario, Entrada  # noqa: E402


class Etapa4(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = dados.carregar(Path(__file__).resolve().parents[1] / "dados", "Bangkok")

    def montar(self, limite, divisao):
        ag = Agencia("Teste", 4, 4, [(0, 1440)] * 7, "b3_45")
        cen = Cenario(ag, self.base.modelos, [], [], self.base.carregadores,
                      {"b3_45": Entrada("b3_45", "B3", 45, 40.5)}, self.base.categorias)
        sub = {"carregadores": {"dc_60x2": 2}, "entrada": "b3_45", "demanda_contratada_kw": None,
               "politica": {"prioridade": "menor_soc", "divisao": divisao, "evitar_ponta": False}}
        m = Motor(cen, sub)
        m.limite_kw = limite
        carros = {
            "geely": Veiculo("geely", self.base.modelos["Geely EX2 Pro"], 2, 30),
            "dolphin": Veiculo("dolphin", self.base.modelos["BYD Dolphin GS"], 3, 50),
            "kwid": Veiculo("kwid", self.base.modelos["Renault Kwid E-Tech"], 1, 40),
            "jac": Veiculo("jac", self.base.modelos["JAC E-JS1"], 1, 75),
        }
        for vid, ponto in (("geely", 0), ("dolphin", 0), ("kwid", 1), ("jac", 1)):
            m.plugar(carros[vid], m.pontos[ponto])
        m.recalcular_potencias(tempo.T0)
        return {k: v.potencia_kw for k, v in carros.items()}

    def test_limite_40_5(self):
        igual = self.montar(40.5, "igual")
        for kw in igual.values():
            self.assertAlmostEqual(kw, 10.125)
        prioridade = self.montar(40.5, "prioridade")
        for nome, esperado in (("kwid", 26.6), ("geely", 13.9), ("jac", 0), ("dolphin", 0)):
            self.assertAlmostEqual(prioridade[nome], esperado)

    def test_limite_80(self):
        igual = self.montar(80, "igual")
        self.assertAlmostEqual(igual["jac"], 16.45)
        for nome in ("geely", "dolphin", "kwid"):
            self.assertAlmostEqual(igual[nome], 21.183333333, places=5)
        prioridade = self.montar(80, "prioridade")
        self.assertAlmostEqual(prioridade["kwid"], 26.6)
        self.assertAlmostEqual(prioridade["geely"], 53.4)
        self.assertAlmostEqual(prioridade["jac"], 0)
        self.assertAlmostEqual(prioridade["dolphin"], 0)


if __name__ == "__main__":
    unittest.main()
