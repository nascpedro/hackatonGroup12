"""Fila, escolha de ponto e curva de carga (regulamento 6.3.2 a 6.3.4)."""
import heapq
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from kickoff import dados, tempo  # noqa: E402
from kickoff.motor import Motor, Veiculo  # noqa: E402
from kickoff.modelo import Agencia, Cenario, Entrada  # noqa: E402


class Etapa3(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = dados.carregar(Path(__file__).resolve().parents[1] / "dados", "Bangkok")

    def motor(self, carregadores):
        ag = Agencia("Teste", 6, 0, [(0, 1440)] * 7, "b3_45")
        cen = Cenario(ag, self.base.modelos, [], [], self.base.carregadores,
                      {"b3_45": Entrada("b3_45", "B3", 45, 40.5)}, self.base.categorias)
        sub = {"carregadores": carregadores, "entrada": "b3_45", "demanda_contratada_kw": None,
               "politica": {"prioridade": "menor_soc", "divisao": "igual", "evitar_ponta": False}}
        m = Motor(cen, sub)
        m.aberta = True
        return m

    def test_dolphin_20_a_80_dc60_em_36_7_minutos(self):
        m = self.motor({"dc_60x2": 1})
        m.limite_kw = 100  # isola a curva e o carregador do limite da agência
        v = Veiculo("v", self.base.modelos["BYD Dolphin GS"], 3, 20)
        m.veiculos[v.id] = v
        m.entrar_patio(v, tempo.T0)
        fim = None
        while m.heap:
            t, _, _, tipo, payload = heapq.heappop(m.heap)
            m.avancar(t)
            if tipo == "fim_recarga":
                m.on_fim_recarga(*payload, t)
            if v.soc >= 80:
                fim = t
                break
        self.assertIsNotNone(fim)
        self.assertAlmostEqual(fim - tempo.T0, 36.7, delta=0.1)

    def test_escolhe_dc60_com_geely_ja_plugado(self):
        m = self.motor({"dc_60x2": 1, "ac_22x2": 1})
        geely = Veiculo("g", self.base.modelos["Geely EX2 Pro"], 2, 30)
        dolphin = Veiculo("d", self.base.modelos["BYD Dolphin GS"], 3, 20)
        dc = next(p for p in m.pontos if p.modelo.id == "dc_60x2")
        m.plugar(geely, dc)
        self.assertIs(m.escolher_ponto(dolphin), dc)

    def test_menor_soc_usa_km_nao_percentual(self):
        m = self.motor({"ac_7": 1})
        a = Veiculo("A", self.base.modelos["Renault Kwid E-Tech"], 1, 30)
        b = Veiculo("B", self.base.modelos["BYD Dolphin Mini GS"], 2, 20)
        m.fila = [b, a]
        m.ordenar_fila(tempo.T0)
        self.assertEqual([v.id for v in m.fila], ["A", "B"])


if __name__ == "__main__":
    unittest.main()
