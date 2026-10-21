# Estado do projeto após a ampliação da validação e a busca inicial

**Data:** 21/10/2026

**Escopo:** simulador local, comparação com o juiz e busca de configurações. Os resultados abaixo cobrem somente as quatro semanas públicas.

## Entregue

- O kit está na raiz do repositório e usa Python 3.10+ com biblioteca padrão. `python3 scripts/check_local.py --strict` roda a suíte e compara três respostas oficiais de Bangkok já salvas, sem rede nem token. O GitHub Actions executa a mesma checagem.
- As etapas 2 a 6 de `kickoff/motor.py` simulam contratos, SOC, fila, recarga, limite elétrico, horários, ponta e políticas. A etapa 7, de eventos ao vivo, continua pendente.
- `scripts/buscar.py` gera submissões válidas, simula cada uma localmente e grava métricas, violações e as cinco primeiras candidatas. A semente e o limite de avaliações tornam a execução reproduzível.
- Há **25 testes locais**, incluindo casos alternativos em Bangkok, Istanbul e Hanoi para verificar contratos, potência máxima, ocupação e energia na ponta.

## Evidência da comparação offline

| Caso de Bangkok | Resultado |
| --- | --- |
| Exemplo original | 271/271 contratos; métricas e séries coincidem com o juiz |
| Um AC-7 e fila intensa | 124 atendidos, 147 perdidos; métricas e séries coincidem |
| Demanda de 80 kW, `proxima_retirada`, ponta evitada, divisão `igual` | Métricas e séries coincidem |
| Mesma política, divisão `prioridade` | Métricas agregadas coincidem; 8 janelas de potência divergem, até 0,041 kW |

As quatro referências vieram de testes gratuitos de Bangkok. As novas chamadas retornaram `taxa: 0` e saldo de **1.000 m7Coins**. A quarta referência está guardada como diagnóstico e não integra a checagem obrigatória enquanto a divergência existir. A comparação com outras agências e com semanas ocultas ainda não foi demonstrada.

## Busca local inicial

| Agência | Configurações válidas simuladas | Sem violações | Sem clientes perdidos |
| --- | ---: | ---: | ---: |
| Bangkok | 48 | 48 | 39 |
| Istanbul | 48 | 48 | 7 |
| Hanoi | 48 | 48 | 16 |

Os arquivos em `resultados/` contêm as avaliações e listas `*_top5.json`. Essa pasta é ignorada pelo Git; cada colega pode reproduzir a rodada com os comandos de `COMANDOS.md`. A ordem das candidatas é uma **heurística provisória**: atendimento e categoria exata, seguidos por aproximações de infraestrutura, pico e energia na ponta. Ela não equivale à nota oficial nem prova desempenho nas semanas ocultas.

## Próximas ações

1. Investigar a divisão `prioridade` no caso divergente de Bangkok e, quando as séries coincidirem, incluí-lo na checagem padrão.
2. Implementar a etapa 7 do motor quando o formato dos eventos ao vivo estiver disponível, seguindo `AGENTS.md` e acrescentando teste da etapa.
3. Evoluir a busca para explorar mais combinações e, após a revelação H4, incorporar custos e pesos oficiais à seleção.
4. Construir o dashboard exigido e preparar configurações finais para cada agência pontuada. Testes pagos exigem autorização da equipe.

**Verificação executada:** `python3 -m unittest discover -s testes`, `python3 simular.py exemplo_submissao.json` e `python3 scripts/check_local.py --strict` passaram em 21/10/2026.
