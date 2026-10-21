"""Retirada, devolução e entrada no pátio (regulamento 4.1 e 6.3.1)."""
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from kickoff.motor import Motor, Veiculo  # noqa: E402
from kickoff.modelo import Agencia, Carregador, Cenario, Entrada, ModeloVeiculo  # noqa: E402


class Etapa2(unittest.TestCase):
    def setUp(self):
        ag = Agencia("Teste", 3, 4, [(0, 1440)] * 7, "b3_45")
        modelo = ModeloVeiculo("Modelo", "Prata", 2, 40, 280, 7, 60, [7] * 20, [60] * 20)
        cen = Cenario(ag, {"Modelo": modelo}, [], [],
                      {"ac_7": Carregador("ac_7", "AC-7", "AC", 7, 1)},
                      {"b3_45": Entrada("b3_45", "B3", 45, 40.5)}, {})
        sub = {"carregadores": {"ac_7": 1}, "entrada": "b3_45",
               "demanda_contratada_kw": None,
               "politica": {"prioridade": "menor_soc", "divisao": "igual", "evitar_ponta": False}}
        self.motor = Motor(cen, sub)
        self.motor.aberta = True
        self.modelo = modelo

    def test_devolucao_usa_km_e_nao_aumenta_soc(self):
        v = Veiculo("v", self.modelo, 2, 80)
        self.assertAlmostEqual(self.motor.soc_devolucao(v, SimpleNamespace(km_devolucao=140)), 50)
        self.assertAlmostEqual(self.motor.soc_devolucao(v, SimpleNamespace(km_devolucao=280)), 80)

    def test_escolha_respeita_categoria_soc_e_plug(self):
        geely = Veiculo("geely", self.modelo, 2, 82)
        dolphin = Veiculo("dolphin", self.modelo, 2, 95, plugado=True)
        mg4 = Veiculo("mg4", self.modelo, 3, 100)
        jac = Veiculo("jac", self.modelo, 1, 100)
        self.motor.patio = {v.id: v for v in (geely, dolphin, mg4, jac)}
        contrato = SimpleNamespace(rank=2)
        self.assertIs(self.motor.escolher_carro(contrato, 0), geely)
        geely.soc = 78
        self.assertIs(self.motor.escolher_carro(contrato, 0), dolphin)
        dolphin.soc = 78
        self.assertIs(self.motor.escolher_carro(contrato, 0), mg4)
        self.motor.aberta = False
        self.assertIsNone(self.motor.escolher_carro(contrato, 0))

    def test_carro_abaixo_do_alvo_entra_na_fila(self):
        v = Veiculo("v", self.modelo, 2, 50)
        self.motor.aberta = False
        self.motor.entrar_patio(v, 123)
        self.assertIs(self.motor.patio["v"], v)
        self.assertEqual(self.motor.fila, [v])
        self.assertEqual(v.entrou_fila_t, 123)


if __name__ == "__main__":
    unittest.main()
