"""Agência fechada e evitar ponta (regulamento 5.2 e 6.3.6)."""
import heapq
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from kickoff import dados, tempo  # noqa: E402
from kickoff.motor import Motor, Veiculo  # noqa: E402
from kickoff.modelo import Agencia, Cenario, Entrada  # noqa: E402


class Etapa5(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = dados.carregar(Path(__file__).resolve().parents[1] / "dados", "Bangkok")

    def montar(self, evitar_ponta=False):
        ag = Agencia("Teste", 1, 2, [(0, 1440)] * 7, "b3_45")
        cen = Cenario(ag, self.base.modelos, [], [], self.base.carregadores,
                      {"b3_45": Entrada("b3_45", "B3", 45, 40.5)}, self.base.categorias)
        sub = {"carregadores": {"ac_11": 1}, "entrada": "b3_45", "demanda_contratada_kw": None,
               "politica": {"prioridade": "chegada", "divisao": "igual", "evitar_ponta": evitar_ponta}}
        m = Motor(cen, sub)
        m.aberta = True
        return m

    def test_carro_pronto_fechado_ocupa_saida_ate_abrir(self):
        m = self.montar()
        v = Veiculo("v", self.base.modelos["MG4 Urban Comfort"], 3, 79)
        m.veiculos[v.id] = v
        m.entrar_patio(v, tempo.T0)
        m.on_fechamento(tempo.T0)
        while m.heap:
            t, _, _, tipo, payload = heapq.heappop(m.heap)
            m.avancar(t)
            if tipo == "fim_recarga":
                m.on_fim_recarga(*payload, t)
        self.assertEqual(v.soc, 80)
        self.assertTrue(v.plugado)
        self.assertEqual(v.potencia_kw, 0)
        m.on_abertura(m.t)
        self.assertFalse(v.plugado)

    def test_evitar_ponta_zera_potencia_sem_desplugar(self):
        m = self.montar(evitar_ponta=True)
        v = Veiculo("v", self.base.modelos["MG4 Urban Comfort"], 3, 29)
        m.veiculos[v.id] = v
        m.entrar_patio(v, tempo.T0)
        self.assertGreater(v.potencia_kw, 0)
        m.on_ponta(True, tempo.T0)
        self.assertEqual(v.potencia_kw, 0)
        self.assertTrue(v.plugado)
        m.on_ponta(False, tempo.T0 + 180)
        self.assertGreater(v.potencia_kw, 0)


if __name__ == "__main__":
    unittest.main()
