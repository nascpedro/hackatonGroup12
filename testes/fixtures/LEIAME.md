# Referência offline de Bangkok

`bangkok_exemplo_juiz.json` é a resposta completa do juiz para
`exemplo_submissao.json`, obtida em 21/10/2026 durante um teste
gratuito de Bangkok autorizado pela equipe (`taxa: 0`). Não contém token.

`python3 scripts/check_local.py`, executado na raiz do projeto, compara a
simulação local com essa resposta sem acessar a API. A opção `--strict`
também exige igualdade de `series.fila_max`.

`bangkok_fila_sub.json` e `bangkok_fila_juiz.json` exercitam um único AC-7,
fila longa, upgrades e 147 clientes perdidos. São a segunda referência oficial
gratuita comparada automaticamente, também com taxa 0 e saldo preservado.

`bangkok_politicas_igual_sub.json` e `bangkok_politicas_igual_juiz.json`
exercitam `proxima_retirada`, ponta evitada, demanda de 80 kW e divisão igual.
São a terceira referência oficial gratuita comparada automaticamente.

`bangkok_politicas_sub.json` e `bangkok_politicas_juiz.json` exercitam
`proxima_retirada`, divisão por prioridade, evitar ponta e demanda de 80 kW.
As métricas agregadas batem, mas 8 janelas de `potencia_kw` divergem até
0,041 kW. Este caso é diagnóstico e ainda não integra a checagem padrão.
