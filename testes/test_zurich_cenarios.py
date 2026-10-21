"""Consistência dos ensaios sintéticos; nenhum dado oculto ou chamada de API."""
import json
import sys
import unittest
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from kickoff import dados, tempo, validar  # noqa: E402
from kickoff.modelo import Agencia, Carregador, Cenario, Contrato, Entrada, ModeloVeiculo, VeiculoT0  # noqa: E402
from scripts.analisar_zurich import avaliar_cenario, gerar_candidatas, gerar_cenarios  # noqa: E402


class CenariosZurich(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalogo = json.loads((RAIZ / "dados/catalogo.json").read_text())
        cls.cenario = dados.carregar(RAIZ / "dados", "Zurich", cls.catalogo)
        cls.casos = {c["nome"]: c for c in gerar_cenarios(cls.cenario)}

    def test_continuacao_preserva_frota_ids_e_duracoes(self):
        caso = self.casos["continuacao"]
        originais = self.cenario.contratos
        contratos = caso["cenario"].contratos
        self.assertEqual(contratos[:len(originais)], originais)
        self.assertEqual(caso["cenario"].veiculos, self.cenario.veiculos)
        self.assertEqual(len(contratos), 2 * len(originais))
        self.assertEqual(len({c.id for c in contratos}), len(contratos))
        delta = tempo.JANELA_PUBLICA[1] - tempo.JANELA_PUBLICA[0]
        for original, copia in zip(originais, contratos[len(originais):]):
            self.assertEqual(copia.retirada_t - original.retirada_t, delta)
            self.assertEqual(copia.devolucao_t - original.devolucao_t, delta)
            self.assertEqual(copia.km_devolucao, original.km_devolucao)
            self.assertTrue(caso["ini"] <= copia.retirada_t < caso["fim"])
        self.assertIs(self.casos["publico"]["cenario"], self.cenario)

    def test_simulacao_continua_sem_reiniciar_soc_da_frota(self):
        ini, _ = tempo.JANELA_PUBLICA
        modelo = ModeloVeiculo("Teste", "Bronze", 1, 40, 200, 7, 30, [0.0] * 20, [0.0] * 20)
        c = Cenario(Agencia("Zurich", 1, 1, [(0, 1440)] * 7, "b3_75"),
                    {"Teste": modelo}, [VeiculoT0("v", "Teste", "Bronze", 1, "estoque_pronto", 80)],
                    [Contrato("c", "Bronze", 1, ini + 60, ini + 120, 0, 0)],
                    {"ac_7": Carregador("ac_7", "AC-7", "AC", 7, 1, 250)},
                    {"b3_75": Entrada("b3_75", "B3", 75, 67.5, 5000)}, {"Bronze": 1})
        sub = {"agencia": "Zurich", "carregadores": {"ac_7": 1}, "entrada": "b3_75",
               "politica": {"prioridade": "chegada", "divisao": "igual", "evitar_ponta": False}}
        casos = {x["nome"]: x for x in gerar_cenarios(c)}
        primeiro = avaliar_cenario(casos["publico"], sub, self.catalogo, [])
        segundo = avaliar_cenario(casos["continuacao"], sub, self.catalogo, [])
        self.assertEqual(primeiro["metricas"]["certos"], 1)
        self.assertEqual(segundo["metricas"]["nao_atendidos"], 1)
        self.assertEqual(segundo["metricas"]["certos"], 0)
        self.assertEqual(c.veiculos[0].soc, 80)

    def test_carga_extra_e_deterministica_sem_ids_duplicados(self):
        n = len(self.cenario.contratos)
        novos = {x["nome"]: x for x in gerar_cenarios(self.cenario)}
        for pct in (5, 10):
            nome = f"demanda_mais_{pct}pct"
            contratos = self.casos[nome]["cenario"].contratos
            self.assertEqual(len(contratos), 2 * n + n * pct // 100)
            self.assertEqual(len({c.id for c in contratos}), len(contratos))
            self.assertEqual(contratos, novos[nome]["cenario"].contratos)

    def test_retiradas_antecipadas_respeitam_abertura_e_devolucao(self):
        n = len(self.cenario.contratos)
        base = self.casos["continuacao"]["cenario"].contratos[n:]
        alterados = self.casos["retiradas_30min_antes"]["cenario"].contratos[n:]
        for a, b in zip(base, alterados):
            self.assertTrue(0 <= a.retirada_t - b.retirada_t <= 30)
            self.assertTrue(tempo.aberta(self.cenario.agencia, b.retirada_t))
            self.assertEqual(a.devolucao_t, b.devolucao_t)
            self.assertLess(b.retirada_t, b.devolucao_t)

    def test_semanas_reordenadas_preservam_categorias_e_duracao(self):
        n = len(self.cenario.contratos)
        contratos = self.casos["semanas_reordenadas"]["cenario"].contratos[n:]
        self.assertEqual(Counter(c.categoria for c in contratos), Counter(c.categoria for c in self.cenario.contratos))
        for original, copia in zip(self.cenario.contratos, contratos):
            self.assertEqual(tempo.dia_semana(original.retirada_t), tempo.dia_semana(copia.retirada_t))
            self.assertEqual(original.devolucao_t - original.retirada_t, copia.devolucao_t - copia.retirada_t)

    def test_pilha_de_candidatas_valida_e_sem_duplicacao(self):
        candidatas = gerar_candidatas(self.cenario)
        self.assertEqual(len({json.dumps(s, sort_keys=True) for s in candidatas}), len(candidatas))
        for s in candidatas:
            self.assertEqual(validar.validar(s, self.cenario), [])


if __name__ == "__main__":
    unittest.main()
