# Conclusões da Análise Exploratória de Dados

**Projeto:** PayFlow Credit Risk  
**Metodologia:** CRISP-DM  
**Fase:** Data Understanding  
**Status:** Análises principais executadas — revisão final pendente

## 1. Objetivo

Investigar o comportamento dos clientes, identificar possíveis relações entre suas características e a inadimplência em até 90 dias, além de avaliar a qualidade dos dados disponíveis.

## 2. Características do dataset

- 5.000 registros de clientes.
- 23 colunas no dataset original.
- 609 clientes classificados em default (12,18%).
- 4.391 clientes sem default (87,82%).
- Nenhuma linha integralmente duplicada.
- Nenhum identificador de cliente duplicado.

A variável-alvo apresenta desbalanceamento entre as classes, característica que deverá ser considerada durante a modelagem e a avaliação.

## 3. Qualidade dos dados

| Verificação | Resultado |
|---|---|
| Renda mensal ausente | 192 registros (3,84%) |
| Tempo de emprego ausente | 526 registros (10,52%) |
| Possíveis outliers de renda pelo IQR | 294 |
| Possíveis outliers de valor solicitado pelo IQR | 335 |
| Duplicatas | Nenhuma identificada |

Os outliers identificados pelo método interquartil não serão automaticamente removidos. Será necessário avaliar sua plausibilidade e o impacto das decisões de tratamento.

## 4. Principais resultados da EDA

### 4.1 Score de crédito

A taxa de default observada foi de 19,37% entre clientes com score de 300 a 500 e 9,44% na faixa de 701 a 800.

Esse resultado sugere uma associação entre score de crédito e inadimplência, mas não demonstra causalidade.

### 4.2 Renda mensal

O menor quartil de renda apresentou taxa de inadimplência de 18,14%, enquanto o maior apresentou 8,15%.

A renda pode fornecer informações relevantes para a análise de risco, mas é necessário considerar os valores ausentes.

### 4.3 Histórico de atrasos

| Maior atraso anterior | Taxa de default |
|---|---:|
| Sem atraso | 8,12% |
| 1–30 dias | 12,61% |
| 31–60 dias | 26,43% |
| 61–90 dias | 41,89% |
| Mais de 90 dias | 63,49% |

O histórico de atrasos apresenta uma associação crescente com a frequência de default.

Essa variável merece atenção na modelagem, desde que os registros sejam anteriores ao momento da decisão de crédito.

### 4.4 Tipo de produto

- BNPL: 15,76% de default.
- Cartão: 12,01%.
- Empréstimo pessoal: 11,24%.

As modalidades apresentaram diferenças na frequência observada de inadimplência. Essas diferenças não devem ser interpretadas automaticamente como efeitos causais do produto.

### 4.5 Utilização do crédito

Clientes na faixa de utilização de até 25% apresentaram 11,41% de default, enquanto aqueles acima de 75% apresentaram 15,53%.

O resultado sugere uma associação que poderá ser investigada na modelagem.

### 4.6 Ausência de renda

A taxa de default foi de 16,15% entre os clientes sem renda informada e de 12,02% entre aqueles com renda preenchida.

Essa diferença observada corresponde a uma diferença absoluta aproximada de 4,1 pontos percentuais. No teste exato de Fisher, o valor de p foi aproximadamente 0,091, o que indica que a evidência não é suficiente para afirmar uma associação estatisticamente significativa ao nível convencional de 5% com os dados disponíveis. A análise deve ser interpretada como sugestão exploratória, não como resultado conclusivo de efeito causal ou de forte associação estatística.

### 4.7 Tempo de emprego para autônomos

Os 526 registros com `tempo_emprego_anos` ausente concentraram-se em trabalhadores autônomos (`autonomo = 1`), o que sugere que a ausência da variável pode refletir uma característica de coleta, e não necessariamente um problema aleatório. A taxa de default foi de 12,55% entre clientes sem tempo de emprego informado e 12,14% entre clientes com esse dado preenchido; a diferença observada foi pequena e não suficiente para sustentar uma interpretação causal.

A mediana global de `tempo_emprego_anos` foi aproximadamente 4,64 anos, enquanto a mediana entre autônomos foi 4,86 anos e entre não autônomos foi 4,62 anos. A proximidade entre as medianas indica que a imputação global pela mediana pode ser uma aproximação aceitável em termos de escala, mas a ausência do dado deve continuar sendo tratada como fenômeno específico, e não como evidência automática de que a mediana global represente a melhor estratégia para todos os grupos.

A estratégia `SimpleImputer(strategy="median", add_indicator=True)` foi testada nos dados de desenvolvimento e não apresentou melhoria mensurável em relação à versão original do pipeline. Portanto, a configuração padrão foi preservada como baseline, e o indicador de ausência foi mantido como opção experimental e não como regra de modelagem definitiva.

## 5. Data Leakage

O dicionário identifica três variáveis com informações posteriores à concessão:

- `parcelas_pagas_ate_3m`
- `atraso_primeira_parcela_dias`
- `status_apos_90d`

Essas colunas não poderão ser utilizadas como preditoras na concessão de crédito.

O identificador `id_cliente` também não será utilizado como variável preditora, e `default_90d` será reservado como target.

## 6. Decisões preliminares para Data Preparation

1. Separar treino e teste antes de ajustar transformações estatísticas.
2. Tratar valores ausentes utilizando somente informações do conjunto de treinamento.
3. Aplicar encoding às variáveis categóricas.
4. Avaliar a necessidade de padronização conforme o algoritmo.
5. Evitar exclusão automática de outliers.
6. Remover das features as informações de futuro.
7. Verificar se as demais variáveis estariam disponíveis na concessão.
8. Preservar o CSV original sem alterações.

## 7. Limitações e pendências

- O dataset é sintético.
- Não há data de concessão identificada no dicionário.
- A regra operacional exata que define default não está completamente especificada.
- As associações exploratórias não comprovam causalidade.
- A relevância preditiva das variáveis deverá ser avaliada em dados separados do treinamento.
- É necessário complementar a investigação dos valores ausentes de tempo de emprego.

## 8. Referências

- FIAP — Análise Exploratória de Dados, Aulas 1 a 4.
- FIAP — Estatística Essencial para Cientistas de Dados.
- FIAP — Introdução ao CRISP-DM.
- `01_auditoria.ipynb`.
- `02_eda.ipynb`.
- `dicionario_dados_payflow.md`.
- `Desafio_Disciplina_PayFlow_Credit_Risk.docx`.