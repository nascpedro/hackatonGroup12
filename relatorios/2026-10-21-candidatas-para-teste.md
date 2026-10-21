# Candidatas H4 para testar no juiz

São as melhores **notas locais na janela pública** com os pesos e custos da H4. Cada link abre um JSON individual pronto para submissão. Istanbul já tem resultado real, indicado abaixo.

| Agência | Submissão | Nota local | Atendimento | Por que testar |
|---|---|---:|---:|---|
| Bangkok (tutorial) | [3 AC-7, B3-45, chegada, evitar ponta, divisão igual](../resultados/h4_submissoes/bangkok.json) | **3.100** | 270/271 | Obra de apenas 750 pontos; perder um contrato compensou frente às opções mais caras. Útil para conferir o simulador sem gastar m7Coins. |
| Istanbul | [1 DC-30 + 3 AC-7, B3-75, próxima retirada, carregar na ponta, divisão igual](../resultados/istanbul_proximo_teste.json) | **8.826,282** | 1.293/1.293 | **Juiz: 8.381,19 e 1.291/1.293.** A obra bateu em 9.250; dois clientes perdidos e energia de ponta maior explicam a diferença. |
| Hanoi | [1 DC-30 + 5 AC-7, B3-75, próxima retirada, carregar na ponta, divisão igual](../resultados/hanoi_finetune_teste.json) | **6.211,016** | 1.166/1.167 | Nova candidata local: obra de 9.750 e um não atendido. A configuração anterior fez **5.457,06 no juiz**, igual à previsão local. [Análise](2026-10-21-hanoi-finetune.md). |
| Marrakech | [9 AC-7 + 1 DC-30, A4-150/130 kW, próxima retirada, evitar ponta, divisão igual](../resultados/marrakech_proximo_teste.json) | **5.793** | 1.230/1.230 | Corte oficial de 30% incluído. Obra de 12.250, 21 upgrades e zero energia na ponta. A alternativa de 120 kW faz 5.806 no evento oficial, mas perdeu três contratos em outro calendário de corte. [Análise](2026-10-21-marrakech-refino-evento.md). |
| Zurich | [2 AC-7 + 1 DC-60 de duas saídas, B3-75 existente, próxima retirada, divisão por prioridade](../resultados/zurich_proximo_teste.json) | **2.252,40** | 859/867 | Obra de 7.800. Na continuação sintética fez 2.768,05 com cinco perdas, contra 1.574,61 e 12 perdas da referência com dois DC-30. Melhorou cinco de seis cenários sintéticos; produção permanece desconhecida. `evitar_ponta=false`. [Análise](2026-10-21-zurich-continuidade.md). |

**Istanbul:** o primeiro teste relatado marcou **6.680** no juiz com obra de 12.500. Se o JSON enviado foi a [configuração anterior](../resultados/h4_submissoes/istanbul.json), a nota local dela era 6.895. Outra política local com a mesma obra (`chegada`, evitar ponta, divisão por prioridade) também marca 6.680; o JSON enviado distinguiria os casos. A [análise do segundo teste](2026-10-21-istanbul-calibracao.md) registra a divergência de 445,09 pontos e os próximos passos.

Nas agências pontuadas, um teste de placar custa 20 m7Coins, e o completo custa 50. As notas locais usam a janela pública; as semanas ocultas podem mudar a escolha. As métricas e alternativas da busca inicial estão em [h4_ranking_local.json](../resultados/h4_ranking_local.json).
