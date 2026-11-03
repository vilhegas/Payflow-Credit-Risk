# Conclusões da Análise Exploratória de Dados

**Projeto:** PayFlow Credit Risk  
**Metodologia:** CRISP-DM  
**Fase:** Data Understanding  
**Status:** Análises exploratórias e revisão metodológica concluídas; limitações e uso histórico do conjunto completo registrados

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

A comparação reproduzível foi executada apenas nos 4.000 registros de desenvolvimento, com cinco folds estratificados idênticos, `random_state=42`, regressão logística e transformações ajustadas dentro de cada fold. A mediana global obteve ROC-AUC média 0,776201 e OOF agregada 0,774315; a mediana com indicadores obteve 0,775194 e 0,773545; a imputação de tempo de emprego pela mediana do grupo de autonomia obteve 0,776274 e 0,774335. No threshold 0,20, o F1 OOF foi respectivamente 0,412241, 0,418395 e 0,412241. Para os indicadores, as diferenças contra a mediana foram precision +0,006003, recall +0,006160, F1 +0,006154, Brier +0,000194 e ROC-AUC OOF −0,000770. Para imputação por grupo, precision, recall e F1 não mudaram; Brier aumentou 0,000001. O indicador trouxe troca pequena entre métricas; os dados não sustentam declarar melhoria geral. A imputação por grupo teve diferenças praticamente nulas e foi mantida como alternativa experimental. A mediana global continua sendo a configuração histórica.

Uma análise complementar de desenvolvimento estimou Average Precision, Brier Skill Score, ablações de features, class weight, correlação juros-score, demonstração separada de leakage e diferenças exploratórias por grupos. Consulte `docs/decisoes_e_limitacoes.md` para a síntese e `reports/experiments/` para resultados completos e parâmetros. Nenhuma feature foi removida automaticamente por pequenas diferenças; as variáveis futuras só foram usadas em experiências didáticas isoladas.

Resultados anteriores citavam ROC-AUC média de aproximadamente 0,7762 e OOF agregada de aproximadamente 0,7743; ambos foram reproduzidos. Também havia uma referência a 0,7652, mas não foi encontrado registro da semente, dos folds, do split ou da configuração que a gerou. Ela não foi reproduzida, e sua origem permanece indeterminada. Os valores e a configuração atuais estão em `reports/experiments/` e podem ser refeitos com `python -m src.experiments.development_validation`.

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
- A validação é aleatória, não temporal, pois não há datas no dataset.
- A análise descritiva original em `02_eda.ipynb` consultou o conjunto completo antes da divisão; isso é preservado como histórico exploratório e não foi usado para seleção dos experimentos de modelagem aqui registrados.

## 8. Referências

- FIAP — Análise Exploratória de Dados, Aulas 1 a 4.
- FIAP — Estatística Essencial para Cientistas de Dados.
- FIAP — Introdução ao CRISP-DM.
- `01_auditoria.ipynb`.
- `02_eda.ipynb`.
- `dicionario_dados_payflow.md`.
- `Desafio_Disciplina_PayFlow_Credit_Risk.docx`.
