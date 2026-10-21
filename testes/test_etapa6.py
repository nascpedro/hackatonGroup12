"""As três políticas de fila (regulamento 6.3.3)."""
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from kickoff import dados  # noqa: E402
from kickoff.motor import Motor, Veiculo  # noqa: E402
from kickoff.modelo import Agencia, Cenario, Entrada  # noqa: E402


class Etapa6(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = dados.carregar(Path(__file__).resolve().parents[1] / "dados", "Bangkok")

    def test_ordens_do_exemplo(self):
        ag = Agencia("Teste", 1, 4, [(0, 1440)] * 7, "b3_45")
        cen = Cenario(ag, self.base.modelos, [], [], self.base.carregadores,
                      {"b3_45": Entrada("b3_45", "B3", 45, 40.5)}, self.base.categorias)
        sub = {"carregadores": {"ac_7": 1}, "entrada": "b3_45", "demanda_contratada_kw": None,
               "politica": {"prioridade": "menor_soc", "divisao": "igual", "evitar_ponta": False}}
        m = Motor(cen, sub)
        carros = [
            Veiculo("A", self.base.modelos["Renault Kwid E-Tech"], 1, 30, entrou_fila_t=600),
            Veiculo("B", self.base.modelos["BYD Dolphin Mini GS"], 2, 20, entrou_fila_t=620),
            Veiculo("C", self.base.modelos["MG4 Urban Comfort"], 3, 55, entrou_fila_t=640),
            Veiculo("D", self.base.modelos["Leapmotor B10 BEV"], 4, 40, entrou_fila_t=655),
        ]
        m.contratos = {c.id: c for c in (
            SimpleNamespace(id="ouro", rank=3, retirada_t=750),
            SimpleNamespace(id="prata", rank=2, retirada_t=795),
            SimpleNamespace(id="bronze", rank=1, retirada_t=840),
        )}
        for prioridade, esperado in (("menor_soc", "ABDC"), ("chegada", "ABCD"),
                                     ("proxima_retirada", "CDBA")):
            m.pol["prioridade"] = prioridade
            m.fila = list(reversed(carros))
            m.ordenar_fila(660)
            self.assertEqual("".join(v.id for v in m.fila), esperado)


if __name__ == "__main__":
    unittest.main()
