# Comandos úteis — Hackathon Recarga Inteligente

Execute os comandos abaixo na pasta `kit_kickoff/`, a partir da raiz deste projeto:

```bash
cd kit_kickoff
```

O projeto usa Python 3.10+ e apenas a biblioteca padrão. Neste ambiente, o executável é `python3`.

## Preparar os dados de Bangkok

Os dados já estão em `dados/Bangkok/`, no caminho padrão do kit:

```bash
python3 -m kickoff.dados Bangkok
```

Para uma agência liberada mais tarde, baixe seu kit com `python3 -m kickoff.api kit NOME_DA_AGENCIA` após configurar a API. Ele será extraído em `dados/NOME_DA_AGENCIA/`.

## Configurar a API nesta sessão do terminal

O token está em `../.env` como `TOKEN=...`. Os comandos abaixo o carregam sem imprimi-lo:

```bash
export GAMEDAY_URL='https://z8tfjfyhgj.execute-api.us-east-1.amazonaws.com/prod'
export GAMEDAY_TOKEN="$(sed -n 's/^TOKEN=//p' ../.env)"
```

Não publique nem versione o arquivo `.env` ou o valor do token. Em cada novo terminal, repita esses dois `export`.

## Verificar status e dados da API

```bash
python3 -m kickoff.api status
python3 -m kickoff.api catalogo dados/catalogo.json
python3 -m kickoff.api kit NOME_DA_AGENCIA
```

- `status`: fase, saldo, agências liberadas, cooldowns e eventos ativos.
- `catalogo`: salva veículos, curvas, carregadores e entradas. Custos e pesos só aparecem a partir de H4; salve o catálogo novamente nessa fase.
- `kit`: baixa os dados de uma agência liberada. Substitua `NOME_DA_AGENCIA` pelo identificador mostrado no status.

O cliente do kit não inclui as rotas de integrantes e placar. Para consultá-las:

```bash
curl -fsS "$GAMEDAY_URL/equipe/integrantes" \
  -H "Authorization: Bearer $GAMEDAY_TOKEN" \
  -H 'Referer: gameday.mobi7.io'

curl -fsS "$GAMEDAY_URL/placar" \
  -H "Authorization: Bearer $GAMEDAY_TOKEN" \
  -H 'Referer: gameday.mobi7.io'
```

Os cinco integrantes informados pela equipe já foram cadastrados. Para cadastrar outro integrante, se necessário:

```bash
curl -fsS -X POST "$GAMEDAY_URL/equipe/integrantes" \
  -H "Authorization: Bearer $GAMEDAY_TOKEN" \
  -H 'Referer: gameday.mobi7.io' \
  -H 'Content-Type: application/json' \
  --data '{"nome":"NOME SOBRENOME"}'
```

## Testar o simulador local

```bash
python3 -m unittest discover -s testes -v
python3 simular.py exemplo_submissao.json
python3 simular.py exemplo_submissao.json --series > dados/bangkok_local_series.json
```

Os 11 testes originais devem executar. O motor em `kickoff/motor.py` ainda contém regras `TODO`; até implementá-las, o resultado local de Bangkok registra 0% de atendimento.

## Comparar com o juiz em Bangkok

Bangkok é tutorial: o teste custa **0 m7Coins**, com cooldown de 1 minuto para uma configuração nova. O teste completo inclui as séries de potência, ocupação e fila.

```bash
python3 -m kickoff.api teste Bangkok exemplo_submissao.json \
  --completo --salvar dados/bangkok_juiz.json > /dev/null

python3 comparar.py exemplo_submissao.json dados/bangkok_juiz.json
```

O comparador mostra a primeira janela de 15 minutos em que o simulador difere do juiz. Seu código de saída é sempre 0; leia a última linha (`OK: bate com o juiz` ou `DIVERGE em: ...`). Para testar outra configuração, copie e edite `exemplo_submissao.json`, depois use **o mesmo arquivo** nos dois comandos.

## Testes em agências pontuadas

Depois de baixar o kit de uma agência e criar uma submissão JSON com o nome correto:

```bash
python3 simular.py dados/minha_submissao.json
python3 -m kickoff.api teste NOME_DA_AGENCIA dados/minha_submissao.json \
  --salvar dados/resposta_placar.json > /dev/null
```

Para receber as séries e comparar o resultado, execute:

```bash
python3 -m kickoff.api teste NOME_DA_AGENCIA dados/minha_submissao.json \
  --completo --salvar dados/resposta_completa.json > /dev/null
python3 comparar.py dados/minha_submissao.json dados/resposta_completa.json
```

Em agências pontuadas, um teste `placar` custa **20 m7Coins**; um `completo`, **50 m7Coins** (ou mais 30 para ampliar um placar já pago). Há cooldown de 5 minutos por agência. Testes idênticos já registrados não cobram novamente. A API limita a equipe a 20 requisições por minuto.

## Eventos e fase H4

Salve o status após um anúncio de evento e passe o mesmo estado ao simulador e ao comparador:

```bash
python3 -m kickoff.api status > dados/status_eventos.json
python3 simular.py dados/minha_submissao.json --eventos dados/status_eventos.json
python3 comparar.py dados/minha_submissao.json dados/resposta_completa.json \
  --eventos dados/status_eventos.json
```

Depois de H4, atualize o catálogo para que o simulador calcule custos e nota:

```bash
python3 -m kickoff.api catalogo dados/catalogo.json
python3 simular.py dados/minha_submissao.json
```

## Envio final

O primeiro envio final de cada agência pontuada é grátis; reenvios custam 80, 160, 320… m7Coins e têm cooldown de 15 minutos. Bangkok não aceita envio final. Faça o envio antes do congelamento e confira a resposta da API:

```bash
curl -fsS -X POST "$GAMEDAY_URL/final/NOME_DA_AGENCIA" \
  -H "Authorization: Bearer $GAMEDAY_TOKEN" \
  -H 'Referer: gameday.mobi7.io' \
  -H 'Content-Type: application/json' \
  --data-binary @dados/minha_submissao.json
```

O campo `agencia` no JSON, se existir, deve ser igual ao nome na rota. Só o último envio final aceito conta para a agência. Sem envio, a agência vale 0 pontos.
