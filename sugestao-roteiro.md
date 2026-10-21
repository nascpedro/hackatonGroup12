# Hackathon Recarga Inteligente — Resumo e roteiro de execução

O hackathon consiste em desenvolver uma solução de otimização para a recarga de veículos elétricos em agências de aluguel de carros, equilibrando atendimento aos clientes, infraestrutura elétrica, custos operacionais e eficiência energética.

O desafio não é simplesmente construir um aplicativo ou um dashboard. O principal é desenvolver um algoritmo capaz de tomar boas decisões, simular os resultados e encontrar configurações que maximizem a pontuação.

## 1. Entendendo o desafio

Cada equipe será responsável por definir como uma rede fictícia de agências deverá operar. Para cada agência, vocês precisam decidir:

- Carregadores: quais modelos instalar e em que quantidade.
- Entrada elétrica: manter ou ampliar a capacidade elétrica da agência.
- Demanda contratada: definir o limite de potência contratado, quando aplicável.
- Política de recarga: escolher quais veículos terão prioridade, como distribuir a potência e se devem evitar recarregar no horário de ponta.

Essas escolhas serão enviadas a um simulador oficial, chamado de juiz, que reproduzirá a operação das agências e calculará uma pontuação.

O objetivo é encontrar uma estratégia que consiga atender o máximo possível de contratos, disponibilizar os veículos nas categorias corretas e minimizar gastos.

O principal desafio está nos trade-offs. Por exemplo, instalar muitos carregadores rápidos pode melhorar o atendimento, mas também aumentar o custo da infraestrutura e a necessidade de potência elétrica. Uma solução mais barata pode economizar recursos, mas perder clientes quando houver muita demanda.

O vencedor será definido principalmente pela qualidade das decisões e pela capacidade de generalizar para cenários desconhecidos, e não pela quantidade de código produzido.

## 2. Como funciona a competição

Duração total

12 horas

Abertura 1h

Jogo 7h30

Apresentações 3h

| Momento    | Atividade                                                   |
| ---------- | ----------------------------------------------------------- |
| H−1 a H0   | Abertura, recebimento da chave da API e testes gratuitos    |
| H0 a H4    | Primeira fase: exploração e desenvolvimento                 |
| H4         | Revelação dos pesos da pontuação e custos de infraestrutura |
| H4 a H7:30 | Otimização, testes e envios finais                          |
| H7:30      | Congelamento das submissões                                 |
| H7:30 a H8 | Preparação das apresentações                                |
| H8 a H11   | Apresentações e premiação                                   |

Os horários são relativos ao início oficial do jogo. O documento informa que a organização controla a passagem das fases, portanto o estado real deve ser consultado na API.

A competição possui 6 agências pontuadas, liberadas progressivamente, além de Bangkok, utilizada como tutorial gratuito.

A classificação geral considera o desempenho nas agências em semanas ocultas, que não são disponibilizadas às equipes durante o desenvolvimento.

## 3. O que será avaliado

A pontuação técnica combina recompensas e penalidades:

| Critério                                 | Efeito              |
| ---------------------------------------- | ------------------- |
| Cliente atendido na categoria solicitada | Positivo            |
| Cliente atendido com upgrade             | Positivo, mas menor |
| Cliente não atendido                     | Negativo            |
| Potência de demanda contratada           | Negativo            |
| Energia consumida na ponta               | Negativo            |
| Investimento em infraestrutura           | Negativo            |

Os valores exatos dos pesos só são revelados em H4. Antes disso, a equipe precisa explorar os cenários e entender quais fatores têm maior influência.

Atenção: o custo de construção é penalizado na nota, mesmo antes de H4, e não é descontado do saldo de testes.

## 4. O que precisa ser desenvolvido e entregue

O regulamento exige um dashboard e uma apresentação. Para produzir bons resultados, também será necessário desenvolver um mecanismo de simulação e otimização.

A. Modelo próprio de simulação e otimização

Implementar as regras do juiz, reproduzindo a dinâmica de disponibilidade dos carros, filas, carregamento, limites elétricos e atendimento aos contratos. Usar esse modelo para comparar configurações sem depender de testes pagos.

Componente estratégico recomendado

B. Otimizador por agência

Escolher uma configuração de carregadores, entrada elétrica, demanda contratada e política de recarga que maximize a pontuação prevista, respeitando as restrições.

Componente estratégico recomendado

C. Dashboard

Exibir por agência as informações exigidas no regulamento: decomposição dos pontos, curva de potência em intervalos de 15 minutos, ocupação das vagas e fila, distribuição de SOC na retirada e clientes perdidos por dia e hora.

Na visão consolidada, apresentar m7Coins gastos, custo de obra, evolução da nota e justificativas das decisões elétricas.

Entregável obrigatório — seção 13.1

D. Apresentação e demonstração

Explicar a estratégia, a inferência dos pesos ocultos, a fidelidade do modelo próprio, as decisões por agência, a reação aos eventos e as melhorias que seriam feitas com mais tempo.

12 minutos de apresentação + 5 minutos de perguntas

Além da classificação geral, existem premiações especiais para melhor dashboard, melhor engenharia elétrica, melhor modelagem e melhor leitura da fase de Neblina.

## 5. Recursos e ferramentas fornecidos

O hackathon já disponibiliza uma infraestrutura inicial:

- Kit de kickoff: arquivos Python, leitores de dados, funções auxiliares, cliente da API e esqueleto de simulador.
- Kits de dados por agência: contratos públicos, estado inicial da frota, catálogo de carregadores e veículos.
- API do juiz: para consultar dados, executar testes e enviar decisões finais.
- Bangkok: agência de treinamento que permite testar gratuitamente sem afetar a classificação.

O regulamento permite qualquer linguagem e o uso de IA generativa. A sugestão é utilizar Python 3.10+, aproveitando o kit inicial, Pandas e NumPy para análise e Streamlit ou Plotly para o dashboard.

Essas bibliotecas adicionais são sugestões minhas, não exigências do regulamento.

## 6. Roteiro de execução recomendado

Minha sugestão é desenvolver o projeto em incrementos, mantendo sempre uma solução funcional. O trabalho deve começar pelo simulador e pela integração com o juiz, deixando o refinamento visual para depois.

Abertura

H−1 a H0

Etapa 1 — Preparação e ambiente

- Baixar `kit_kickoff.zip` e o kit de Bangkok.
- Configurar Python, dependências e repositório Git.
- Ler `LEIAME.md` e a documentação da API.
- Executar `simular.py exemplo_submissao.json`.
- Fazer um teste gratuito em Bangkok e executar `comparar.py`.
- Dividir as responsabilidades da equipe.

Meta: ambiente funcional e comunicação com o juiz validada.

Fase 1

H0–H2

Etapa 2 — Construção do simulador

Completar o motor fornecido, priorizando:

- Processamento cronológico das devoluções e retiradas.
- SOC inicial e recarga até o limite fixo de 80%.
- Seleção do veículo adequado a cada contrato.
- Gestão de vagas, carregadores e fila.
- Cálculo de potência, curvas AC/DC e limites da agência.
- Restrições de horário de funcionamento e ponta.

Comparar os resultados com o juiz usando Bangkok. Começar com cenários simples antes de avançar para os complexos.

Meta: simular a operação com fidelidade razoável.

Fase 2

H2–H4

Etapa 3 — Otimização inicial e exploração

- Implementar um gerador de configurações válidas.
- Comparar carregadores AC, DC e combinações.
- Testar as políticas de fila e distribuição de potência.
- Avaliar cenários com diferentes limites elétricos.
- Investigar os efeitos dos parâmetros sobre a nota.
- Iniciar o dashboard com dados de simulação.

Como os pesos ainda são ocultos, manter alternativas conservadoras e agressivas, em vez de depender de uma única hipótese.

Meta: obter boas configurações candidatas para cada agência.

Fase 3

H4–H6

Etapa 4 — Ajuste com os pesos oficiais

Após H4:

- Importar pesos e custos publicados.
- Implementar a função de pontuação exata conhecida.
- Executar buscas locais em torno das melhores configurações.
- Usar os testes pagos de forma seletiva.
- Identificar erros do simulador pela comparação com o juiz.
- Realizar envios finais gratuitos quando existir uma solução suficientemente boa.

Meta: converter os experimentos em configurações competitivas.

Fase 4

H6–H7:30

Etapa 5 — Consolidação e envios finais

- Garantir que todas as seis agências tenham envios finais aceitos.
- Monitorar eventos operacionais e alterações do cenário.
- Verificar se os reenvios justificam seus custos.
- Finalizar os gráficos obrigatórios.
- Conferir o placar e os retornos da API.

Meta: nenhuma agência sem submissão e dashboard completo.

Final

H7:30+

Etapa 6 — Apresentação

Preparar demonstração do dashboard, resultados do modelo, estratégias escolhidas e trade-offs. Ensaiar os 12 minutos de apresentação e preparar respostas para os 5 minutos de perguntas.

## 7. Arquitetura sugerida

Para ganhar velocidade, usaria uma aplicação Python modular, sem necessidade de microsserviços ou backend complexo.

Dados das agências + API do juiz

Contratos, frota, catálogo, avaliações

Simulador

Eventos, recarga, disponibilidade

Otimizador

Geração e busca de configurações

Resultados e experimentos

Métricas, pontuações e comparações

Dashboard + gerador de submissões JSON

Visualização, decisões e apresentação

O núcleo seria um simulador determinístico de eventos discretos. O otimizador utilizaria esse simulador para testar centenas ou milhares de configurações locais, sem gastar m7Coins. Uma abordagem inicial seria busca aleatória com validação de restrições, seguida de busca local nos melhores candidatos.

## 8. Cuidado com o orçamento de testes

Cada equipe começa com 1.000 m7Coins. O uso do juiz possui os seguintes custos:

| Operação                         | Custo  |
| -------------------------------- | ------ |
| Teste Bangkok                    | Grátis |
| Teste padrão (`placar`)          | 20     |
| Teste completo                   | 50     |
| Primeiro envio final por agência | Grátis |
| Segundo envio final              | 80     |
| Terceiro envio final             | 160    |
| Quarto envio final               | 320    |

Os testes pagos têm cooldown de 5 minutos por agência e os reenvios finais, de 15 minutos. O saldo não entra na pontuação.

Minha sugestão é reservar uma parcela significativa do orçamento para as agências que forem liberadas mais tarde. Não gastaria tudo tentando otimizar as primeiras agências, especialmente antes de H4.

## 9. Divisão de responsabilidades

Para uma equipe de quatro pessoas, distribuiria assim:

| Responsável | Área principal                              |
| ----------- | ------------------------------------------- |
| Pessoa 1    | Integração com a API e tratamento dos dados |
| Pessoa 2    | Motor de simulação e fidelidade ao juiz     |
| Pessoa 3    | Algoritmos de otimização e experimentos     |
| Pessoa 4    | Dashboard, métricas e apresentação          |

O desenvolvimento do simulador e do otimizador deve acontecer em paralelo, mas com uma interface bem definida entre eles.

## 10. Checklist de conclusão

Progresso do projeto

0 de 10

API autenticada e dados das agências carregados

Simulador próprio executando os cenários

Resultados comparados com o juiz de Bangkok

Gerador de configurações válidas funcionando

Otimizador executando buscas e registrando resultados

Pesos e custos de H4 incorporados ao modelo

Dashboard com todos os gráficos obrigatórios

Eventos operacionais considerados

Seis agências com envios finais aceitos

Apresentação preparada e ensaiada

## Recomendação de prioridade

A ordem que eu seguiria é:

1\. Simulador fiel → 2. Otimização → 3. Testes com o juiz → 4. Dashboard → 5. Apresentação.

Embora o dashboard seja obrigatório, ele não deve consumir o tempo inicialmente destinado ao desenvolvimento do algoritmo. A melhor estratégia é garantir primeiro uma solução que funcione, depois uma que pontue bem e, por fim, uma que comunique claramente o trabalho realizado.

O ponto de maior potencial técnico é conseguir reproduzir o comportamento do juiz com baixo erro e usar esse modelo para encontrar boas soluções gastando poucos m7Coins. Isso contribui tanto para a classificação geral quanto para o prêmio especial de melhor modelagem.