# Hackathon Recarga Inteligente — Grupo 12

Repositório de trabalho da equipe para modelar a recarga de agências de locação de veículos elétricos. As escolhas de carregadores, entrada elétrica, demanda e política são avaliadas pelo simulador oficial. O objetivo é atender os contratos com boa nota e generalizar para as semanas ocultas.

## Onde está cada coisa

| Caminho | Conteúdo |
|---|---|
| [`REGULAMENTO.md`](REGULAMENTO.md) | Regulamento oficial obtido em `GET /instrucoes` em 21/10/2026; consultar a API para atualizações e o anexo H4 |
| [`dados/Bangkok/`](dados/Bangkok/) | Dados públicos da agência tutorial: 80 veículos, 271 contratos, carregadores, entradas e curvas |
| [`dados/Istanbul/`](dados/Istanbul/) | Dados públicos da agência pontuada: 235 veículos, 1.293 contratos e 4 vagas elétricas |
| [`dados/Hanoi/`](dados/Hanoi/) | Dados públicos da agência pontuada: 305 veículos, 1.167 contratos e 6 vagas elétricas |
| [`dados/Marrakech/`](dados/Marrakech/) | Dados públicos da agência pontuada: 480 veículos, 1.230 contratos e 10 vagas elétricas |
| [`dados/Zurich/`](dados/Zurich/) | Dados públicos da agência pontuada: 255 veículos, 867 contratos e 4 vagas elétricas |
| [`dados/Vienna/`](dados/Vienna/) | Dados públicos da agência H5: 300 veículos, 864 contratos, 30 vagas e operação 24h |
| [`kickoff/`](kickoff/) | Simulador, cliente da API e módulos fornecidos no kickoff |
| [`COMANDOS.md`](COMANDOS.md) | Preparação do ambiente e comandos para dados, API, testes e comparação |
| [`.env.example`](.env.example) | Formato do arquivo local do token; preencher `.env` apenas na própria máquina |

## Vienna — H5, 21/10/2026

Kit baixado, catálogo atualizado e cenário de consistência incluído no pipeline local. A melhor candidata nas 54 avaliações públicas foi **4 AC-7, A4-150 existente, demanda de 30 kW, próxima retirada e evitar ponta**: **11.900 pontos locais**, 864 atendimentos na categoria certa e nenhum perdido. A referência de produção informada pela equipe é 11.800; as semanas ocultas não estão disponíveis para comparação direta.

O [JSON pronto para teste](resultados/vienna_proximo_teste.json) e a [análise de parâmetros](relatorios/2026-10-21-vienna.md) estão no projeto. Para reproduzir, sem API:

```bash
python3 -m kickoff.dados Vienna
python3 simular.py resultados/vienna_proximo_teste.json --eventos dados/status_vienna.json
python3 scripts/check_local.py --strict
```

## Registro da preparação inicial — 21/10/2026

- Equipe **#12** cadastrada na API. Na consulta de 21/10/2026, a fase era **Neblina**; Bangkok, Istanbul, Hanoi, Marrakech e Zurich estavam liberadas em `GET /status`.
- O teste oficial **gratuito** da submissão `exemplo_submissao.json` em Bangkok foi válido, sem violações: **271/271 contratos atendidos**, pico de **40,5 kW** e **4.512,24 kWh** nas semanas públicas. A nota retornada foi **14,475**, calculada pelo juiz com pesos ainda ocultos. O saldo permaneceu em **1.000 m7Coins**.
- O simulador local implementa retirada, devolução, recarga, limites elétricos, horário, ponta e as três prioridades. No exemplo de Bangkok ele reproduz os **271 atendimentos**, o pico, a energia e todas as séries de 15 minutos do juiz. A apresentação de `fila_max` foi inferida da resposta oficial salva e ainda precisa ser validada em outras configurações. Eventos ao vivo aguardam o formato anunciado pela organização.
- Há **28 testes locais** e três comparações exatas com respostas oficiais gratuitas de Bangkok salvas em `testes/fixtures/`: o exemplo, uma fila intensa e uma política alternativa com divisão igual. Um quarto caso, com divisão por prioridade, revelou uma diferença pequena em 8 janelas de potência e está documentado na pasta de referências. As checagens locais não usam a PalavraChave nem gastam m7Coins.
- `scripts/buscar.py` gera submissões válidas, avalia configurações localmente e preserva as avaliações completas e a fronteira provisória de soluções não dominadas. Uma rodada de 48 candidatas por agência em Bangkok, Istanbul e Hanoi foi salva em `resultados/` (artefatos locais ignorados pelo Git). `scripts/reclassificar.py` calcula a nota local com custos e pesos oficiais quando o catálogo H4 estiver disponível, sem repetir as simulações. O catálogo salvo ainda não contém esses dados.
- Nenhum envio final foi feito nesta preparação. Bangkok é tutorial e não pontua.

## Próximas etapas

1. Investigar a pequena divergência de potência do caso de políticas alternativas de Bangkok e acrescentar novas referências oficiais gratuitas quando útil.
2. Implementar eventos ao vivo quando o formato de cada evento for anunciado, com testes locais antes de comparar com o juiz.
3. Procurar configurações válidas localmente para Marrakech e Zurich; quando outras agências forem liberadas, baixar seus kits. Usar testes pagos só com autorização da equipe e reservar saldo para agências tardias e reenvios.
4. Montar o dashboard obrigatório: cascata de pontos, potência versus limite/ponta, ocupação/fila, SOC na retirada, perdas por horário e evolução da nota.
5. Após H4, atualizar o catálogo com pesos e custos, revisar as decisões e fazer um envio final por agência pontuada antes do congelamento.

Os testes avaliam quatro semanas públicas; os envios finais são julgados em quatro semanas ocultas. Evitem escolher uma configuração apenas por um bom resultado no período público. O primeiro envio final por agência é gratuito, mas reenvios custam m7Coins.

## Começar

Use Python 3.10 ou superior, sem dependências externas. Na raiz do projeto, execute:

```bash
python3 scripts/check_local.py --strict
```

O comando roda a suíte e compara todas as métricas e séries de três casos de Bangkok com referências oficiais salvas. O fluxo automático em `.github/workflows/local-check.yml` executa o mesmo comando, **sem API ou token**. Siga [`COMANDOS.md`](COMANDOS.md) para comandos manuais e busca local. O arquivo `.env` está ignorado pelo Git; **nunca inclua a PalavraChave em commits, mensagens ou capturas**.
