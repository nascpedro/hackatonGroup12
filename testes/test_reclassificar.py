"""Reclassificação com catálogo H4 sintético, sem API e sem alterar o catálogo real."""
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from scripts import reclassificar  # noqa: E402


class Reclassificacao(unittest.TestCase):
    def setUp(self):
        self.catalogo = {
            "pesos": {"Bangkok": {"certo": 10, "upgrade": 5, "nao_atendido": -50,
                                   "demanda_contratada": -2, "energia_ponta_kwh": -1,
                                   "infraestrutura": -3}},
            "carregadores": [{"id": "ac_7", "custo": 1}, {"id": "dc_60x2", "custo": 100}],
            "entradas": [{"id": "a4_150", "custo": 200}],
        }
        self.barata = {"agencia": "Bangkok", "carregadores": {"ac_7": 1},
                       "entrada": "b3_45"}
        self.cara = {"agencia": "Bangkok", "carregadores": {"dc_60x2": 1},
                     "entrada": "a4_150", "demanda_contratada_kw": 80}
        self.metricas = {"certos": 10, "upgrades": 0, "nao_atendidos": 0,
                         "energia_ponta_kwh": 0}

    def relatorio(self):
        return {"agencia": "Bangkok", "periodo": "publico", "resultados": [
            {"submissao": self.cara, "metricas": {**self.metricas, "demanda_contratada_kw": 80},
             "violacoes": []},
            {"submissao": self.barata, "metricas": {**self.metricas, "demanda_contratada_kw": 0},
             "violacoes": []},
        ]}

    def test_nota_oficial_reordena_mesmo_com_atendimento_igual(self):
        resultado = reclassificar.reclassificar(self.relatorio(), self.catalogo,
                                               RAIZ / "dados", "hash-teste")
        self.assertEqual(resultado["catalogo_sha256"], "hash-teste")
        self.assertEqual([r["submissao"] for r in resultado["resultados"]],
                         [self.barata, self.cara])
        self.assertEqual([r["nota"] for r in resultado["resultados"]], [97, -960])
        self.assertEqual(resultado["resultados"][0]["custo_infra"]["total"], 1)
        self.assertEqual(resultado["resultados"][1]["custo_infra"]["total"], 300)

    def test_catalogo_pre_h4_e_recusado(self):
        with self.assertRaisesRegex(ValueError, "pesos oficiais completos"):
            reclassificar.reclassificar(self.relatorio(), {}, RAIZ / "dados")
        incompleto = {**self.catalogo, "entradas": []}
        with self.assertRaisesRegex(ValueError, "sem custo oficial"):
            reclassificar.reclassificar(self.relatorio(), incompleto, RAIZ / "dados")


if __name__ == "__main__":
    unittest.main()
