# Hackathon Recarga Inteligente — Grupo 12

Repositório de trabalho da equipe para modelar a recarga de agências de locação de veículos elétricos. As escolhas de carregadores, entrada elétrica, demanda e política são avaliadas pelo simulador oficial. O objetivo é atender os contratos com boa nota e generalizar para as semanas ocultas.

## Onde está cada coisa

| Caminho | Conteúdo |
|---|---|
| [`REGULAMENTO.md`](REGULAMENTO.md) | Regulamento oficial obtido em `GET /instrucoes` em 21/10/2026; consultar a API para atualizações e o anexo H4 |
| [`dados/Bangkok/`](dados/Bangkok/) | Dados públicos da agência tutorial: 80 veículos, 271 contratos, carregadores, entradas e curvas |
| [`dados/Istanbul/`](dados/Istanbul/) | Dados públicos da agência pontuada: 235 veículos, 1.293 contratos e 4 vagas elétricas |
| [`dados/Hanoi/`](dados/Hanoi/) | Dados públicos da agência pontuada: 305 veículos, 1.167 contratos e 6 vagas elétricas |
| [`kickoff/`](kickoff/) | Simulador, cliente da API e módulos fornecidos no kickoff |
| [`COMANDOS.md`](COMANDOS.md) | Preparação do ambiente e comandos para dados, API, testes e comparação |
| [`.env.example`](.env.example) | Formato do arquivo local do token; preencher `.env` apenas na própria máquina |

## Estado atual — 21/10/2026

- Equipe **#12** cadastrada na API. A fase é **Neblina (H0)**; Bangkok, Istanbul e Hanoi estão liberadas em `GET /status`.
- O teste oficial **gratuito** da submissão `exemplo_submissao.json` em Bangkok foi válido, sem violações: **271/271 contratos atendidos**, pico de **40,5 kW** e **4.512,24 kWh** nas semanas públicas. A nota retornada foi **14,475**, calculada pelo juiz com pesos ainda ocultos. O saldo permaneceu em **1.000 m7Coins**.
- O simulador local implementa retirada, devolução, recarga, limites elétricos, horário, ponta e as três prioridades. No exemplo de Bangkok ele reproduz os **271 atendimentos**, o pico, a energia e todas as séries de 15 minutos do juiz. A apresentação de `fila_max` foi inferida da resposta oficial salva e ainda precisa ser validada em outras configurações. Eventos ao vivo aguardam o formato anunciado pela organização.
- Há **25 testes locais** e três comparações exatas com respostas oficiais gratuitas de Bangkok salvas em `testes/fixtures/`: o exemplo, uma fila intensa e uma política alternativa com divisão igual. Um quarto caso, com divisão por prioridade, revelou uma diferença pequena em 8 janelas de potência e está documentado na pasta de referências. As checagens locais não usam a PalavraChave nem gastam m7Coins.
- `scripts/buscar.py` gera submissões válidas e avalia configurações localmente. Uma rodada inicial de 48 candidatas por agência em Bangkok, Istanbul e Hanoi foi salva em `resultados/` (artefatos locais ignorados pelo Git). A ordenação usa uma heurística provisória, pois custos e pesos oficiais ainda não estavam no catálogo salvo.
- Nenhum envio final foi feito nesta preparação. Bangkok é tutorial e não pontua.

## Próximas etapas

1. Investigar a pequena divergência de potência do caso de políticas alternativas de Bangkok e acrescentar novas referências oficiais gratuitas quando útil.
2. Implementar eventos ao vivo quando o formato de cada evento for anunciado, com testes locais antes de comparar com o juiz.
3. Quando outras agências forem liberadas, baixar os kits, procurar configurações válidas localmente e usar testes pagos para validar candidatas promissoras. Reservar saldo para agências tardias e reenvios.
4. Montar o dashboard obrigatório: cascata de pontos, potência versus limite/ponta, ocupação/fila, SOC na retirada, perdas por horário e evolução da nota.
5. Após H4, atualizar o catálogo com pesos e custos, revisar as decisões e fazer um envio final por agência pontuada antes do congelamento.

Os testes avaliam quatro semanas públicas; os envios finais são julgados em quatro semanas ocultas. Evitem escolher uma configuração apenas por um bom resultado no período público. O primeiro envio final por agência é gratuito, mas reenvios custam m7Coins.

## Começar

Use Python 3.10 ou superior, sem dependências externas. Na raiz do projeto, execute:

```bash
python3 scripts/check_local.py --strict
```

O comando roda a suíte e compara todas as métricas e séries de três casos de Bangkok com referências oficiais salvas. O fluxo automático em `.github/workflows/local-check.yml` executa o mesmo comando, **sem API ou token**. Siga [`COMANDOS.md`](COMANDOS.md) para comandos manuais e busca local. O arquivo `.env` está ignorado pelo Git; **nunca inclua a PalavraChave em commits, mensagens ou capturas**.
