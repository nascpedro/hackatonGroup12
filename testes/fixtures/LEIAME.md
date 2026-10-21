# Referência offline de Bangkok

`bangkok_exemplo_juiz.json` é a resposta completa do juiz para
`exemplo_submissao.json`, obtida em 21/10/2026 durante um teste
gratuito de Bangkok autorizado pela equipe (`taxa: 0`). Não contém token.

`python3 scripts/check_local.py`, executado na raiz do projeto, compara a
simulação local com essa resposta sem acessar a API. A opção `--strict`
também exige igualdade de `series.fila_max`.
