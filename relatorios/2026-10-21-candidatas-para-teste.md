# Candidatas H4 para testar no juiz

São as melhores **notas locais na janela pública** entre 79–82 configurações distintas avaliadas por agência, usando os pesos e custos da H4. Cada link abre um JSON individual pronto para submissão. **Ainda não foram testadas no juiz nesta rodada.**

| Agência | Submissão | Nota local | Atendimento | Por que testar |
|---|---|---:|---:|---|
| Bangkok (tutorial) | [3 AC-7, B3-45, chegada, evitar ponta, divisão igual](../resultados/h4_submissoes/bangkok.json) | **3.100** | 270/271 | Obra de apenas 750 pontos; perder um contrato compensou frente às opções mais caras. Útil para conferir o simulador sem gastar m7Coins. |
| Istanbul | [2 DC-30 + 2 AC-7, B3-75, próxima retirada, evitar ponta, divisão igual](../resultados/h4_submissoes/istanbul.json) | **6.895** | 1.293/1.293 | Atendimento integral na categoria certa, sem energia de ponta e sem demanda contratada; obra de 12.500. |
| Hanoi | [1 AC-22x2 + 1 DC-30 + 3 AC-7, B3-75, próxima retirada, divisão por prioridade](../resultados/h4_submissoes/hanoi.json) | **5.457,061** | 1.167/1.167 | Nenhum perdido, obra de 10.750 e sem cobrança de demanda; superou localmente as instalações A4 mais caras. `evitar_ponta=false`. |
| Marrakech | [3 AC-7 + 2 AC-22x2 + 1 DC-30, A4-150/110 kW, próxima retirada, evitar ponta, divisão por prioridade](../resultados/h4_submissoes/marrakech.json) | **1.875** | 1.220/1.230 | Melhor nota local mesmo com o corte publicado de 30% no limite elétrico; zera a energia de ponta. É a **primeira prioridade de validação**, pois a implementação do evento ainda não foi comparada com o juiz. |
| Zurich | [2 AC-7 + 2 DC-30, B3-75 existente, próxima retirada, divisão por prioridade](../resultados/h4_submissoes/zurich.json) | **2.341,193** | 858/867 | A entrada existente não custa obra; os nove perdidos ainda deixam esta opção acima das instalações mais caras avaliadas. `evitar_ponta=false`. |

**Ordem sugerida para testes reais:** Bangkok como controle gratuito; depois Marrakech e Zurich, onde há mais incerteza; por fim Hanoi e Istanbul. Nas agências pontuadas, um teste de placar custa 20 m7Coins, e o completo custa 50. Os resultados acima são estimativas da janela pública; as semanas ocultas podem mudar a escolha. As métricas e alternativas estão em [h4_ranking_local.json](../resultados/h4_ranking_local.json).
