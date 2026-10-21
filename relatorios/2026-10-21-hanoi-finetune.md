# Hanoi: ajuste local após o primeiro placar

O [placar resumido do juiz](../resultados/hanoi_juiz_placar_resumo.json) marcou **5.457,06** para a [configuração anterior](../resultados/h4_submissoes/hanoi.json), igual à nota prevista pelo simulador local até os centavos exibidos. As métricas de atendimento e custo também batem; a diferença de 0,0019 kWh na energia de ponta ao rodar `comparar.py` decorre do arredondamento da captura. Isso aumenta a confiança na comparação offline para Hanoi, mas não garante que toda variante vá coincidir.

## Melhor candidata encontrada

[JSON pronto para teste](../resultados/hanoi_finetune_teste.json): **1 DC-30 + 5 AC-7, B3-75, próxima retirada, carregar na ponta, divisão igual**. Todos os seis pontos são de uma saída e a potência instalada soma 65 kW, abaixo do limite útil de 67,5 kW da entrada. Por isso, `igual` e `prioridade` tiveram o mesmo resultado local.

| Métrica | Anterior: juiz e local | Nova: previsão local |
|---|---:|---:|
| Nota | 5.457,06 | **6.211,02** |
| Certos / upgrades / não atendidos | 1.161 / 6 / 0 | **1.156 / 10 / 1** |
| Energia na ponta | 2.511,88 kWh | **2.517,97 kWh** |
| Custo de infraestrutura | 10.750 | **9.750** |

O ganho previsto é **753,96 pontos**: economiza 1.000 na obra, perde 243 pela mudança nos atendimentos e cerca de 3,04 pela energia adicional na ponta. A previsão fica **448,06 pontos** acima da referência de placar de 5.762,96 informada pela equipe. Dois clientes adicionais perdidos em relação à previsão tirariam aproximadamente 430 pontos, deixando uma margem de apenas 18,06; a nota real ainda precisa ser medida.

## Busca offline

Foram avaliadas [20 combinações próximas](../resultados/hanoi_finetune_candidatas.json) de carregadores e divisão de potência ([resultados](../resultados/hanoi_finetune_avaliacoes.json)), além das [12 políticas](../resultados/hanoi_finetune_politicas_avaliacoes.json) para o conjunto vencedor. A alternativa **1 DC-30 + 1 AC-11 + 4 AC-7** ficou em 5.396,54; **1 AC-22x2 + 1 DC-30 + 3 AC-7** permaneceu em 5.457,06. Manter a entrada B3-45 existente com o conjunto anterior causou 257 não atendidos mesmo na melhor divisão testada, então não é uma economia viável. Para o novo conjunto, `chegada` marcou 5.123,67, `menor_soc` 1.533,77 e `evitar_ponta=true` no máximo 2.967,00.

As avaliações foram feitas apenas com `simular.py` e o catálogo H4 local. Nenhuma chamada à API paga foi feita nesta busca. Reproduzir a candidata: `python3 simular.py resultados/hanoi_finetune_teste.json`.
