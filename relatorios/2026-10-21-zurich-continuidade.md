# Zurich: mudar a seleção para continuidade e disponibilidade

**Primeiro teste indicado:** [1 DC-60 de duas saídas + 2 AC-7, B3-75 existente, próxima retirada, divisão por prioridade, carregar na ponta](../resultados/zurich_proximo_teste.json). Obra de **7.800**, apenas 300 acima dos 7.500 atuais. Previsão pública: **2.252,40**, com oito perdidos. Na continuação sintética, marcou **2.768,05**, com cinco perdidos, contra **1.574,61 e 12 perdidos** da configuração atual.

São ensaios locais, não previsões da produção. A queda de cerca de 1.900 no teste oficial para 100–200 na produção foi relatada pela equipe; não há resposta detalhada oficial de Zurich salva para calibrar essa diferença.

## O que mudou na abordagem

Foram avaliadas **342 configurações públicas**, incluindo famílias DC com três ou quatro saídas e obra de até 11.500, políticas, controles só AC, quatro DC-30 e ampliações A4. Depois, **21 candidatas passaram por sete cenários**, somando **147 simulações adicionais**. Não há prova de ótimo global nem probabilidades estimadas para esses cenários.

A seleção passou a considerar a frota depois de quatro semanas de uso. Nos cenários de continuação, o motor roda desde T0 com os contratos públicos originais e cópias para as semanas 5–8; a nota é calculada só nessa segunda janela. **O SOC e a frota não são reiniciados.** As semanas ocultas reais não foram acessadas.

## Comparação principal

Todos os casos abaixo usam B3-75, próxima retirada, divisão por prioridade e carregam na ponta. Cada célula mostra **nota / não atendidos**.

| Cenário | Atual: 2 DC-30 + 2 AC-7 | Indicada: 1 DC-60x2 + 2 AC-7 | Melhor pública: 1 DC-60x2 + 1 AC-7 |
|---|---:|---:|---:|
| Público original | 2.341,19 / 9 | **2.252,40 / 8** | **2.990,37 / 6** |
| Continuação sem reiniciar frota | 1.574,61 / 12 | **2.768,05 / 5** | 1.546,76 / 12 |
| Continuação com 43 reservas extras (~5%) | −3.082,64 / 36 | −2.556,29 / 33 | −1.968,35 / 31 |
| Continuação com 86 reservas extras (~10%) | −9.773,75 / 70 | **−7.928,49 / 60** | −8.824,11 / 66 |
| Devoluções com 10% menos km de autonomia | 845,34 / 15 | **1.622,16 / 10** | 1.255,61 / 13 |
| Retiradas até 30 min antes, dentro do horário | 1.422,87 / 13 | **1.734,09 / 10** | 287,65 / 18 |
| Semanas públicas reordenadas: 2, 4, 1, 3 | **−2.868,35 / 32** | −4.196,72 / 37 | −2.875,25 / 32 |

A indicada melhorou **cinco dos seis cenários sintéticos** em relação à atual. Ela piorou na reordenação das semanas; não domina a referência em todos os casos. Nenhuma das 21 candidatas manteve nota positiva em todos os cenários. A alternativa de três saídas vence na janela pública, mas caiu mais nas retiradas antecipadas e não melhorou a continuação.

Os cenários extras repetem o mesmo tráfego público com alterações explícitas: reservas adicionais em horários existentes, menos autonomia devolvida, antecipação limitada pela abertura ou outra ordem das semanas. Cada janela recebe o custo completo de infraestrutura. Os resultados não estimam a frequência dessas situações nas semanas ocultas.

## Diagnóstico e motivo da escolha

- A configuração atual começou a janela pública sem perdas na primeira semana; na primeira semana da continuação perdeu cinco. Isso mostra sensibilidade ao estado herdado da frota no cenário construído.
- Nas 12 perdas da continuação atual, sete foram de Diamante. Algumas perdas ocorreram com fila de 30–32 carros, quatro plugados e potência próxima de 67,5 kW. Há pressão de capacidade e disponibilidade por categoria.
- O DC-60x2 mantém duas saídas e pode concentrar mais de 30 kW em um veículo quando curva e repartição permitem. A potência nominal total continua **74 kW**, igual à atual; o ganho vem da distribuição da potência e das decisões de recarga, respeitando os mesmos 67,5 kW da entrada.
- Chegada e menor SOC não melhoraram a seleção final: com DC-60x2 + dois AC-7, chegada perdeu 20–21 contratos na continuação; menor SOC, 43–45; próxima retirada por prioridade, cinco.
- Mais infraestrutura não resolveu o equilíbrio econômico: três DC-30 + um AC-7 marcaram −464,78 no público; quatro DC-30, −3.045,43 na melhor política; a melhor ampliação A4 entre os controles marcou −4.974,07. A entrada existente custa zero de obra e deve ser preservada na candidata indicada.

Cada atendimento certo que vira perdido reduz a nota em **215 pontos**. Nove perdas adicionais custam 1.935, mantendo os demais termos. A obra da mesma configuração é fixa por janela; variações no número e no perfil dos contratos, atendimentos e energia podem consumir a margem. O ensaio não demonstra quais desses fatores causaram a queda oficial relatada.

## Reproduzir e usar

[Busca pública completa](../resultados/zurich_busca_robusta.json), [21 finalistas](../resultados/zurich_finalistas.json), [147 avaliações com diagnósticos](../resultados/zurich_cenarios_robustos.json) e [resumo CSV](../resultados/zurich_resumo_cenarios.csv). O [JSON de maior nota pública](../resultados/zurich_maior_nota_publica.json) fica como alternativa de comparação, com três saídas.

```bash
python3 scripts/analisar_zurich.py busca --eventos dados/eventos_zurich.json --saida resultados/zurich_busca_robusta.json
python3 scripts/analisar_zurich.py cenarios --submissoes resultados/zurich_finalistas.json --eventos dados/eventos_zurich.json --saida resultados/zurich_cenarios_robustos.json
python3 simular.py resultados/zurich_proximo_teste.json --eventos dados/eventos_zurich.json
```

O script usa quatro processos locais por padrão (`--jobs 1` executa em sequência), biblioteca padrão e hashes do catálogo e dos arquivos do kit. Não lê `.env` nem chama a API. O snapshot usado não tem eventos para Zurich. Se houver novo anúncio, atualizar o arquivo de eventos antes de nova decisão.

Foram adicionados seis testes: continuidade efetiva do SOC, IDs e períodos das cópias, reservas extras reproduzíveis, abertura nas antecipações, duração dos contratos reordenados e validade das candidatas. O motor e os módulos protegidos não foram alterados. **Nenhuma chamada à API ou envio final foi feito nesta análise.**
