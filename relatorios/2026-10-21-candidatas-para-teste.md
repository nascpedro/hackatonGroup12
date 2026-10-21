# Candidatas H4 para testar no juiz

São as melhores **notas locais na janela pública** com os pesos e custos da H4. Cada link abre um JSON individual pronto para submissão. A candidata nova de Istanbul ainda não foi testada no juiz.

| Agência | Submissão | Nota local | Atendimento | Por que testar |
|---|---|---:|---:|---|
| Bangkok (tutorial) | [3 AC-7, B3-45, chegada, evitar ponta, divisão igual](../resultados/h4_submissoes/bangkok.json) | **3.100** | 270/271 | Obra de apenas 750 pontos; perder um contrato compensou frente às opções mais caras. Útil para conferir o simulador sem gastar m7Coins. |
| Istanbul | [1 DC-30 + 3 AC-7, B3-75, próxima retirada, carregar na ponta, divisão igual](../resultados/istanbul_proximo_teste.json) | **8.826,282** | 1.293/1.293 | Obra de 9.250, nenhum perdido e três upgrades; a energia na ponta custa cerca de 1.298 pontos, mas a economia de obra compensa. |
| Hanoi | [1 AC-22x2 + 1 DC-30 + 3 AC-7, B3-75, próxima retirada, divisão por prioridade](../resultados/h4_submissoes/hanoi.json) | **5.457,061** | 1.167/1.167 | Nenhum perdido, obra de 10.750 e sem cobrança de demanda; superou localmente as instalações A4 mais caras. `evitar_ponta=false`. |
| Marrakech | [3 AC-7 + 2 AC-22x2 + 1 DC-30, A4-150/110 kW, próxima retirada, evitar ponta, divisão por prioridade](../resultados/h4_submissoes/marrakech.json) | **1.875** | 1.220/1.230 | Melhor nota local mesmo com o corte publicado de 30% no limite elétrico; zera a energia de ponta. É a **primeira prioridade de validação**, pois a implementação do evento ainda não foi comparada com o juiz. |
| Zurich | [2 AC-7 + 2 DC-30, B3-75 existente, próxima retirada, divisão por prioridade](../resultados/h4_submissoes/zurich.json) | **2.341,193** | 858/867 | A entrada existente não custa obra; os nove perdidos ainda deixam esta opção acima das instalações mais caras avaliadas. `evitar_ponta=false`. |

**Istanbul:** o teste relatado marcou **6.680** no juiz com obra de 12.500. Se o JSON enviado foi a [configuração anterior](../resultados/h4_submissoes/istanbul.json), a nota local dela era 6.895. Outra política local com a mesma obra (`chegada`, evitar ponta, divisão por prioridade) também marca 6.680; convém conferir o JSON enviado antes de atribuir a diferença ao motor. A nova opção veio de 72 simulações locais adicionais e supera 8.500 mesmo se um atendimento certo virar perdido, desde que os outros termos da nota não mudem.

Nas agências pontuadas, um teste de placar custa 20 m7Coins, e o completo custa 50. As notas locais usam a janela pública; as semanas ocultas podem mudar a escolha. As métricas e alternativas da busca inicial estão em [h4_ranking_local.json](../resultados/h4_ranking_local.json).
