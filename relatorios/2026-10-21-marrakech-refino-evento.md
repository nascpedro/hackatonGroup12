# Marrakech: parâmetros com o corte ativo

**Primeiro teste recomendado:** [1 DC-30 + 9 AC-7, A4-150, demanda de 130 kW, próxima retirada, evitar ponta e divisão igual](../resultados/marrakech_proximo_teste.json). A previsão é **5.793 pontos nas semanas públicas**, com 1.209 certos, 21 upgrades e nenhum perdido. Os **6.898 informados pela equipe são da produção**, nas semanas ocultas, e não permitem comparação direta com esta previsão.

## Evento e parâmetros

Status e catálogo foram confirmados por GET na H5 de 21/10/2026. O [arquivo de eventos](../dados/eventos_marrakech.json) contém exatamente `['corte', 'Marrakech', 31680, 34560, 0.7]`: de **08/11/2049 00:00 a 10/11/2049 00:00**, com 134 retiradas públicas nesse intervalo. Todas as 133 configurações da busca usaram esse evento.

Na recomendação, o limite passa de **130 para 91 kW** durante o corte e depois volta a 130. Os carregadores somam **93 kW nominais e dez saídas**, dentro das dez vagas. A demanda acima da potência instalada serve para manter mais potência durante o corte: com 120 kW contratados, o limite cairia para 84 kW.

O motor já aplicava essa regra. Foi acrescentado um teste para conferir que, em A4, o corte usa a **demanda contratada**, limita a potência efetiva a 91 kW e restaura o limite no fim. Nenhuma regra do motor foi alterada.

## Resultado da busca

| Configuração | Nota local com evento oficial | Perdidos / upgrades | Obra |
|---|---:|---:|---:|
| Anterior: 2 AC-22x2 + 5 AC-7 + 1 DC-30, 130 kW, prioridade | 3.814 | 0 / 18 | 14.250 |
| **Recomendada: 9 AC-7 + 1 DC-30, 130 kW, igual** | **5.793** | **0 / 21** | **12.250** |
| [Alternativa: mesmos carregadores, 120 kW, prioridade](../resultados/marrakech_maior_nota_local.json) | **5.806** | 0 / 22 | 12.250 |

Todas usam A4-150, próxima retirada e evitam ponta. O ganho da recomendação é **1.979 pontos**: economiza 2.000 na obra e perde 21 por três upgrades adicionais. Energia de ponta permanece zero. A conta é `1.209 × 15 + 21 × 8 − 2 × 130 − 12.250 = 5.793`.

As opções só com AC perderam muitos contratos; a melhor delas nesta busca perdeu 71. Manter B3-75 com 1 DC-30 + 9 AC-7 também não compensou: perdeu 98 na melhor política testada. Reduzir para oito AC-7 na A4 chegou a 5.472, com dois perdidos. A busca não prova ótimo global.

## Por que recomendar 130 kW para produção

Também simulei **o mesmo tráfego público** movendo as 48 horas de corte para segunda e terça de cada semana. São cenários sintéticos de sensibilidade; não representam os contratos ocultos nem preveem a nota de produção.

| Semana do corte | 120 kW / prioridade: nota, perdidos | 130 kW / igual: nota, perdidos |
|---|---:|---:|
| 1 | 5.813; 0 | 5.793; 0 |
| 2 | 5.834; 0 | 5.772; 0 |
| 3 | 5.063; 3 | 5.807; 0 |
| 4 — evento oficial | 5.806; 0 | 5.793; 0 |

A opção de 130 kW abriu mão de só **13 pontos** na janela oficial e preservou o atendimento nos quatro cortes testados. Por isso é minha indicação inicial para o objetivo de produção. No cenário adicional sem corte, ambas perderam um contrato; as decisões discretas de alocação tornam o resultado sensível ao calendário, e esses ensaios não garantem generalização.

## Arquivos e reprodução

As 90 avaliações de arquiteturas e políticas e as 43 de demanda estão consolidadas no [ranking](../resultados/marrakech_refino_evento_ranking.json), com hash do catálogo e evento aplicado. Os [cenários de sensibilidade](../resultados/marrakech_sensibilidade.json) guardam as quinze simulações adicionais. Não há referência oficial de Marrakech para calibrar esses resultados.

```bash
python3 simular.py resultados/marrakech_proximo_teste.json --eventos dados/eventos_marrakech.json
python3 simular.py resultados/marrakech_refino_evento_candidatas.json --eventos dados/eventos_marrakech.json
python3 simular.py resultados/marrakech_demanda_candidatas.json --eventos dados/eventos_marrakech.json
```

Nenhum teste pago ou envio final foi feito nesta preparação. O próximo passo é medir a candidata no juiz e preservar a resposta para comparação.
