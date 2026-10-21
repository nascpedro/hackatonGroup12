# Istanbul: calibração após o segundo placar

**Configuração testada:** [1 DC-30 + 3 AC-7, B3-75, próxima retirada, carregar na ponta, divisão igual](../resultados/istanbul_proximo_teste.json). O [placar oficial transcrito](../resultados/istanbul_juiz_placar_resumo.json) contém apenas os números da captura de tela; não há série temporal ou eventos do juiz.

| Métrica | Simulador local | Juiz | Efeito na nota |
|---|---:|---:|---:|
| Nota | 8.826,28 | **8.381,19** | −445,09 |
| Certos / upgrades / não atendidos | 1.290 / 3 / 0 | **1.288 / 3 / 2** | −430,00 |
| Energia na ponta | 2.595,44 kWh | **2.625,61 kWh** | −15,09 |
| Infraestrutura | 9.250 | **9.250** | 0 |
| Pico | 51 kW | **51 kW** | Não entra diretamente na nota |

Cada contrato que passa de certo a não atendido reduz a nota em 215 pontos: perde 15 pelo acerto e recebe −200. Os dois casos explicam 430 dos 445,09 pontos de diferença. Os 30,17 kWh extras na ponta explicam os 15,09 restantes. O custo da obra está correto. A energia total difere em 72,39 kWh, mas não pontua diretamente e pode ser consequência das retiradas diferentes. Os valores exibidos pelo juiz têm arredondamento.

**Meta de 8.500:** faltam 118,81 pontos. Recuperar um dos dois clientes perdidos, mantendo os demais itens, levaria o placar a aproximadamente **8.596,19**. Alcançar a meta só com energia na ponta exigiria reduzir cerca de **237,62 kWh** (9,1%) sem perder mais contratos.

## O que já foi explorado localmente

- Trocar `divisao` para `prioridade` dá o mesmo resultado local: os carregadores instalados somam no máximo 51 kW, abaixo dos 67,5 kW úteis da B3-75. O limite da entrada não força repartição.
- `evitar_ponta=true` com a instalação atual caiu para aproximadamente 7.299 pontos locais e 12 não atendidos.
- Retirar um AC-7 economiza 250 pontos de obra, mas causou 36 não atendidos e nota local de aproximadamente 1.045.
- Mais 60 simulações de cinco conjuntos de carregadores baratos não superaram a configuração atual. A melhor dessas alternativas, 1 DC-30 + 1 AC-22x2 + 1 AC-7, marcou 7.786,78 pontos locais com obra de 10.250. Dados em [candidatas](../resultados/istanbul_baratas_candidatas.json) e [avaliações](../resultados/istanbul_baratas_avaliacoes.json). A busca não prova ótimo global.

## Próximos passos

1. **Manter 8.381,19 como referência oficial** e a configuração atual como a melhor validada. Evitar gastar 20 m7Coins em mudanças de `divisao` que não alteram a potência local.
2. **Diagnosticar os dois contratos perdidos antes de mexer no motor.** As três comparações offline disponíveis de Bangkok continuam batendo com o juiz, mas não garantem Istanbul. Uma resposta `completo` do mesmo teste, se o grupo decidir gastar os 30 m7Coins adicionais, permitiria comparar séries e localizar a primeira divergência com `comparar.py`. Não foi feita nenhuma chamada paga nesta análise.
3. **Corrigir apenas a regra demonstradamente divergente**, caso a trilha detalhada mostre diferença no motor; então repetir os testes locais e comparar novamente. Se os contratos perdidos decorrerem de uma configuração, procurar outra combinação que preserve quatro saídas e reduza a energia na ponta ou melhore a disponibilidade no instante crítico.

Para reproduzir a comparação com o placar resumido: `python3 comparar.py resultados/istanbul_proximo_teste.json resultados/istanbul_juiz_placar_resumo.json`.
