# Comandos úteis — Hackathon Recarga Inteligente

## Pipeline local, sem token

Na raiz do projeto:

```bash
python3 scripts/check_local.py --strict
```

Esse comando roda os testes e compara todas as métricas e séries de três casos de
Bangkok com respostas oficiais já salvas. Não lê `.env` nem chama a API. O mesmo
comando roda no GitHub Actions, sem secrets.

Os testes locais também cobrem cenários alternativos em Bangkok, Istanbul,
Hanoi e Vienna: conservação dos contratos, limite de potência, vagas e energia na ponta.
Esses cenários verificam consistência interna; as três referências salvas de
Bangkok foram comparadas com o juiz. Para acrescentar outra resposta oficial
**já salva**:

```bash
python3 scripts/check_local.py --strict \
  --caso caminho/submissao.json caminho/resposta_oficial.json
```

Para iniciar uma busca reproduzível de configurações válidas, sem API:

```bash
python3 scripts/buscar.py Bangkok --base exemplo_submissao.json \
  --max-avaliacoes 48 --seed 12 --saida resultados/bangkok.json
python3 scripts/buscar.py Istanbul --max-avaliacoes 48 --seed 12 \
  --saida resultados/istanbul.json
python3 scripts/buscar.py Hanoi --max-avaliacoes 48 --seed 12 \
  --saida resultados/hanoi.json
```

O JSON guarda **todas** as submissões, métricas e violações. O comando também
grava `*_fronteira.json`, com as soluções não dominadas pelos objetivos
provisórios, e `*_top5.json`, uma lista de consulta. Ambos podem ser passados
diretamente a `simular.py`. A fronteira usa atendimento, categoria exata,
demanda, energia na ponta e aproximações de infraestrutura. Pico e energia
total ficam apenas como métricas de diagnóstico: não entram diretamente na nota.
`resultados/` guarda os artefatos da busca. Nenhuma ordenação pré-H4 equivale à nota do
juiz; preserve o JSON completo para a reclassificação.

Depois de H4, atualize `dados/catalogo.json` com custos e pesos oficiais e
reclassifique **sem ressimular** as avaliações já salvas:

```bash
python3 scripts/reclassificar.py resultados/bangkok.json --catalogo dados/catalogo.json
python3 scripts/reclassificar.py resultados/istanbul.json --catalogo dados/catalogo.json
python3 scripts/reclassificar.py resultados/hanoi.json --catalogo dados/catalogo.json
```

O comando recusa um catálogo sem os seis pesos ou os custos usados pelas
submissões. Ele grava `*_pontuado.json` com a decomposição da nota e o hash do
catálogo, além de `*_pontuado_top5.json`. Se os pesos mudarem, rode a
reclassificação novamente. Se eventos operacionais alterarem a simulação,
gere novas avaliações antes de reclassificar. A nota é calculada das métricas
**locais das semanas públicas**, não das semanas ocultas.

Os comandos manuais abaixo também são executados na raiz do repositório.

O projeto usa Python 3.10+ e apenas a biblioteca padrão. Neste ambiente, o executável é `python3`.

## Preparar os dados de Bangkok

Os dados já estão em `dados/Bangkok/`, no caminho padrão do kit:

```bash
python3 -m kickoff.dados Bangkok
```

Para uma agência liberada mais tarde, baixe seu kit com `python3 -m kickoff.api kit NOME_DA_AGENCIA` após configurar a API. Ele será extraído em `dados/NOME_DA_AGENCIA/`.

## Vienna: ambiente local da H5

O kit já está em `dados/Vienna/`; o catálogo inclui seus pesos. A captura de status
em `dados/status_vienna.json` não contém eventos para Vienna. Para simular a
recomendação e refazer as 54 avaliações, sem rede ou token:

```bash
python3 -m kickoff.dados Vienna
python3 simular.py resultados/vienna_proximo_teste.json --eventos dados/status_vienna.json
python3 simular.py resultados/vienna_candidatas.json --eventos dados/status_vienna.json > resultados/vienna_avaliacoes.json
python3 scripts/check_local.py --strict
```

A candidata usa **4 AC-7**, entrada **A4-150 existente**, demanda explícita de
**30 kW**, prioridade `proxima_retirada`, `evitar_ponta=true` e divisão `igual`.
Nota pública local: **11.900**, sem perdidos ou upgrades. Omitir a demanda vale
130 kW e desconta mais 200 pontos sem aumentar a potência desses carregadores.
O [relatório de Vienna](relatorios/2026-10-21-vienna.md) explica as alternativas e
a diferença entre teste público e nota final nas semanas ocultas.

## Marrakech: simular com o corte ativo

O evento está em `dados/eventos_marrakech.json`: limite multiplicado por 0,7
entre os minutos 31680 e 34560. Use o arquivo em todas as simulações da agência:

```bash
python3 simular.py resultados/marrakech_proximo_teste.json --eventos dados/eventos_marrakech.json
```

A recomendação usa **1 DC-30 + 9 AC-7, A4-150, 130 kW**, próxima retirada,
evitar ponta e divisão igual. Prevê **5.793 pontos públicos** com nenhum perdido;
durante o corte o limite é 91 kW. A variante de 120 kW marca 5.806, mas foi mais
sensível à mudança do calendário do corte. Parâmetros, busca e comparação estão
no [relatório de Marrakech](relatorios/2026-10-21-marrakech-refino-evento.md).

## Zurich: busca e cenários de continuidade, sem API

A seleção de Zurich considera a nota pública e o comportamento da frota nas
semanas seguintes. O script abaixo usa apenas dados locais, com quatro processos
por padrão. Use `--jobs 1` para executar em sequência.

```bash
python3 scripts/analisar_zurich.py busca --eventos dados/eventos_zurich.json --saida resultados/zurich_busca_robusta.json
python3 scripts/analisar_zurich.py cenarios --submissoes resultados/zurich_finalistas.json --eventos dados/eventos_zurich.json --saida resultados/zurich_cenarios_robustos.json
python3 simular.py resultados/zurich_proximo_teste.json --eventos dados/eventos_zurich.json
```

Foram avaliadas 342 configurações públicas e 21 finalistas em sete cenários.
Os cenários repetem ou alteram contratos públicos e **não preveem as semanas
ocultas**. A continuação preserva o estado da frota, sem reiniciar o SOC.

A candidata indicada usa **1 DC-60 de duas saídas + 2 AC-7, B3-75 existente**,
próxima retirada, divisão por prioridade e `evitar_ponta=false`: 2.252,40 pontos
públicos e 2.768,05 na continuação sintética. O snapshot utilizado não tem eventos
para Zurich. Resultados, alternativas e limitações estão no
[relatório de Zurich](relatorios/2026-10-21-zurich-continuidade.md).

## Configurar a API nesta sessão do terminal

O token está em `.env` como `TOKEN=...`. Os comandos abaixo o carregam sem imprimi-lo:

```bash
export GAMEDAY_URL='https://z8tfjfyhgj.execute-api.us-east-1.amazonaws.com/prod'
export GAMEDAY_TOKEN="$(sed -n 's/^TOKEN=//p' .env)"
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

Os 36 testes locais devem passar. O exemplo de Bangkok reproduz as métricas
físicas e séries de 15 minutos do juiz para a referência salva.

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
