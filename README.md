# Hackathon Recarga Inteligente — Grupo 12

Repositório de trabalho da equipe para modelar a recarga de agências de locação de veículos elétricos. As escolhas de carregadores, entrada elétrica, demanda e política são avaliadas pelo simulador oficial. O objetivo é atender os contratos com boa nota e generalizar para as semanas ocultas.

## Onde está cada coisa

| Caminho | Conteúdo |
|---|---|
| [`REGULAMENTO.md`](REGULAMENTO.md) | Regulamento oficial obtido em `GET /instrucoes` em 21/10/2026; consultar a API para atualizações e o anexo H4 |
| [`kit_kickoff/dados/Bangkok/`](kit_kickoff/dados/Bangkok/) | Dados públicos da agência tutorial: 80 veículos, 271 contratos, carregadores, entradas e curvas |
| [`kit_kickoff/dados/Istanbul/`](kit_kickoff/dados/Istanbul/) | Dados públicos da agência pontuada: 235 veículos, 1.293 contratos e 4 vagas elétricas |
| [`kit_kickoff/dados/Hanoi/`](kit_kickoff/dados/Hanoi/) | Dados públicos da agência pontuada: 305 veículos, 1.167 contratos e 6 vagas elétricas |
| [`kit_kickoff/`](kit_kickoff/) | Simulador inicial, cliente da API, comparador e testes fornecidos no kickoff |
| [`COMANDOS.md`](COMANDOS.md) | Preparação do ambiente e comandos para dados, API, testes e comparação |
| [`.env.example`](.env.example) | Formato do arquivo local do token; preencher `.env` apenas na própria máquina |

## Estado atual — 21/10/2026

- Equipe **#12** cadastrada na API. A fase é **Neblina (H0)**; Bangkok, Istanbul e Hanoi estão liberadas em `GET /status`.
- O teste oficial **gratuito** da submissão `kit_kickoff/exemplo_submissao.json` em Bangkok foi válido, sem violações: **271/271 contratos atendidos**, pico de **40,5 kW** e **4.512,24 kWh** nas semanas públicas. A nota retornada foi **14,475**, calculada pelo juiz com pesos ainda ocultos. O saldo permaneceu em **1.000 m7Coins**.
- O simulador local ainda é um **esqueleto**. Com a mesma submissão, ele registra 0% de atendimento; os métodos `TODO` de `kit_kickoff/kickoff/motor.py` precisam ser implementados. Os 11 testes originais passam; Istanbul e Hanoi também carregam no leitor do kit.
- Nenhum envio final foi feito nesta preparação. Bangkok é tutorial e não pontua.

## Próximas etapas

1. Completar o motor por etapas: retirada/devolução, fila/recarga, limite de potência, horário/ponta, políticas e eventos. Adicionar testes com os exemplos do regulamento.
2. Comparar as métricas e séries de 15 minutos do motor com `POST /teste/Bangkok?detalhe=completo` até reproduzir o juiz em configurações diferentes.
3. Quando outras agências forem liberadas, baixar os kits, procurar configurações válidas localmente e usar testes pagos para validar candidatas promissoras. Reservar saldo para agências tardias e reenvios.
4. Montar o dashboard obrigatório: cascata de pontos, potência versus limite/ponta, ocupação/fila, SOC na retirada, perdas por horário e evolução da nota.
5. Após H4, atualizar o catálogo com pesos e custos, revisar as decisões e fazer um envio final por agência pontuada antes do congelamento.

Os testes avaliam quatro semanas públicas; os envios finais são julgados em quatro semanas ocultas. Evitem escolher uma configuração apenas por um bom resultado no período público. O primeiro envio final por agência é gratuito, mas reenvios custam m7Coins.

## Começar

Use Python 3.10 ou superior, sem dependências externas. Siga [`COMANDOS.md`](COMANDOS.md) para preparar `dados/Bangkok`, executar a suíte e consultar a API. O arquivo `.env` está ignorado pelo Git; **nunca inclua a PalavraChave em commits, mensagens ou capturas**.
