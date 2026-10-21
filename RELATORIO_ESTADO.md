# Estado da implementação — 21/10/2026

## O que já temos

- **Ambiente reproduzível:** o kit está na raiz do repositório, usa Python 3.10+ e apenas a biblioteca padrão. `python3 scripts/check_local.py --strict` executa os testes, simula Bangkok e compara os resultados com três respostas oficiais salvas. O GitHub Actions roda essa mesma checagem sem token e sem consumir m7Coins.
- **Dados e integração:** os dados públicos de Bangkok, Istanbul e Hanoi estão organizados em `dados/`. Há cliente para consultar a API e obter os kits. Os cinco integrantes informados pela equipe foram cadastrados.
- **Simulador:** as etapas 2 a 6 de `kickoff/motor.py` estão implementadas. Elas cobrem escolha e devolução de carros, SOC, fila e prioridades, escolha de carregador, curva de recarga, divisão de potência, limite elétrico, horário de funcionamento e ponta. Os módulos de leitura, validação, medição e nota do kit continuam disponíveis.
- **Validação:** há 25 testes locais. A checagem `--strict` reproduz exatamente três respostas oficiais gratuitas de Bangkok: o exemplo (271 atendimentos), um caso de fila intensa (124 atendimentos, 147 perdas) e uma política alternativa com divisão igual. Há testes de consistência física para políticas alternativas em Bangkok, Istanbul e Hanoi. A checagem atual não chama a API.
- **Busca inicial:** 48 configurações válidas foram simuladas por agência em Bangkok, Istanbul e Hanoi. Os relatórios completos e listas das cinco primeiras candidatas ficam em `resultados/`, ignorado pelo Git. A seleção usa uma heurística provisória, sem custos ou pesos oficiais.

## Limites da validação

A comparação exata cobre **três configurações de Bangkok**. Uma quarta referência gratuita, com `proxima_retirada`, divisão por prioridade e ponta evitada, coincide nas métricas agregadas, mas diverge em 8 janelas de potência (diferença máxima de 0,041 kW). A mesma configuração com divisão `igual` coincide exatamente, isolando a divergência na divisão por prioridade. O caso divergente está guardado como diagnóstico em `testes/fixtures/`. A fidelidade em outras agências e semanas ocultas ainda não está demonstrada. A consulta à API nesta data indicou fase Neblina e saldo de 1.000 m7Coins; os novos testes de Bangkok custaram 0.

## Próximos passos, em ordem

1. **Concluir a etapa 7 do motor:** implementar os eventos ao vivo em `agendar_eventos` e `on_evento` quando houver formato e casos concretos, com um teste por etapa e as duas verificações exigidas em `AGENTS.md`.
2. **Resolver a divergência do caso de políticas alternativas:** localizar a diferença nas janelas de 25/10 e incorporar essa referência à checagem padrão quando reproduzida exatamente. Priorizar testes gratuitos e não executar testes pagos sem autorização da equipe.
3. **Evoluir a busca inicial para um otimizador:** ampliar a exploração do espaço de configurações, registrar experimentos e selecionar candidatas que funcionem bem em diferentes semanas. O roteiro de ideias está em `sugestao-roteiro.md`.
4. **Incorporar a revelação H4:** atualizar custos e pesos do catálogo quando disponíveis e reordenar as candidatas pelo critério de pontuação vigente.
5. **Entregar o dashboard e preparar os envios finais:** mostrar os indicadores exigidos pelo regulamento, verificar as candidatas pontuadas e garantir um envio final válido para cada agência antes do congelamento. Bangkok é tutorial e não pontua.

**Prioridade imediata:** esclarecer a divergência de potência e usar a busca local para selecionar candidatas robustas. Os resultados públicos de Bangkok ainda não bastam para afirmar equivalência geral com o juiz.
