# Metas de Negócio e Metas Analíticas

**Projeto:** Credit Risk — Score de Inadimplência  
**Metodologia:** CRISP-DM  
**Fase:** Business Understanding  
**Status:** Planejamento

---

## 1. Objetivo

Definir indicadores que permitam avaliar se a solução de previsão de inadimplência em até 90 dias contribui para decisões de crédito mais consistentes.

O modelo deverá ser avaliado por sua capacidade preditiva e pelo potencial de apoiar resultados financeiros.

## 2. Metas de negócio (KPIs)

Os KPIs representam os resultados que a empresa deseja melhorar.

| KPI | Objetivo | Forma de avaliação |
|---|---|---|
| Taxa de inadimplência em 90 dias | Reduzir a proporção de clientes inadimplentes | Clientes em default / clientes avaliados na carteira |
| Perda financeira esperada | Reduzir a exposição financeira ao risco de crédito | Estimativa de perdas associadas à inadimplência |
| Taxa de aprovação | Preservar a capacidade sustentável de concessão | Solicitações aprovadas / solicitações avaliadas |
| Custo operacional de cobrança | Melhorar o planejamento e a eficiência | Custo de cobrança em relação ao volume de operações |

Esses indicadores são propostas para avaliar o problema. O desafio não fornece metas financeiras numéricas nem valores reais de perda e recuperação.

## 3. Metas analíticas

As métricas analíticas avaliam o desempenho do modelo de classificação.

| Métrica | Finalidade |
|---|---|
| Recall | Medir a proporção de inadimplentes corretamente identificados |
| Precision | Medir quantos clientes classificados como alto risco realmente apresentam default |
| ROC-AUC | Avaliar a capacidade de discriminar clientes com e sem default |
| Calibração | Verificar se as probabilidades estimadas correspondem às frequências observadas |
| Matriz de confusão | Identificar acertos e erros por classe |
| Custo por erro | Avaliar o impacto das decisões incorretas |

A acurácia também poderá ser calculada, mas não deverá ser utilizada isoladamente como critério de seleção.

## 4. Fórmulas de avaliação

### 4.1 Recall

Recall = TP / (TP + FN)

Onde:

- TP: clientes inadimplentes corretamente identificados como alto risco.
- FN: clientes inadimplentes incorretamente identificados como baixo risco.

Um recall elevado significa que o modelo identifica uma parcela maior dos casos de inadimplência.

### 4.2 Precision

Precision = TP / (TP + FP)

Onde:

- TP: inadimplentes corretamente identificados.
- FP: clientes não inadimplentes classificados incorretamente como alto risco.

Uma precision elevada indica menor proporção de alertas incorretos entre as classificações de alto risco.

### 4.3 F1-Score

F1 = 2 × (Precision × Recall) / (Precision + Recall)

Combina precision e recall por meio de uma média harmônica.

### 4.4 Acurácia

Acurácia = (TP + TN) / (TP + TN + FP + FN)

Representa a proporção total de classificações corretas.

Como a inadimplência é a classe minoritária no dataset, essa métrica será interpretada juntamente com outras medidas.

### 4.5 Perda esperada

Uma formulação financeira complementar é:

EL = PD × LGD × EAD

Onde:

- PD: probabilidade de default.
- LGD: percentual da exposição perdido em caso de default.
- EAD: exposição financeira no momento do default.

O modelo poderá fornecer uma estimativa de PD. Entretanto, o dicionário de dados não disponibiliza diretamente LGD ou EAD, de modo que não será possível calcular a perda esperada real sem informações ou hipóteses adicionais.

**Nota:** a fórmula de perda esperada é uma proposta técnica complementar para operacionalizar o KPI financeiro; não é uma fórmula explicitamente fornecida no enunciado.

## 5. Falsos positivos e falsos negativos

### Falso positivo (FP)

O modelo classifica um cliente como alto risco, embora ele não apresente default.

Possível consequência: rejeitar ou submeter a revisão adicional uma solicitação potencialmente saudável.

### Falso negativo (FN)

O modelo classifica um cliente como baixo risco, embora ele apresente default.

Possível consequência: conceder crédito a uma operação que posteriormente gera inadimplência.

O custo de cada erro deverá ser considerado na escolha do threshold.

## 6. Definição do threshold

O threshold é o limite utilizado para converter uma probabilidade estimada em uma classificação.

Exemplo ilustrativo:

- Probabilidade estimada: 0,65.
- Threshold hipotético: 0,50.
- Resultado: cliente classificado como alto risco.

O valor de 0,50 será apenas uma referência inicial.

A escolha final deverá considerar:

1. Recall e precision;
2. Quantidade de falsos positivos e falsos negativos;
3. Calibração das probabilidades;
4. Custos financeiros e operacionais;
5. Restrições e objetivos da política de crédito.

O threshold será selecionado usando dados de validação, sem otimização sobre o conjunto de teste final.

## 7. Critérios de sucesso

O desafio não estabelece valores mínimos obrigatórios para recall, ROC-AUC ou redução de perdas.

Portanto, os critérios serão definidos após estabelecer uma referência inicial e avaliar os dados.

A solução deverá:

- Superar um baseline relevante;
- Apresentar capacidade de discriminação mensurável;
- Produzir probabilidades cuja calibração seja avaliada;
- Permitir análise explícita dos custos de classificação;
- Utilizar somente informações disponíveis no momento da decisão;
- Apresentar desempenho documentado em dados separados do treinamento.

Nenhuma meta de desempenho será declarada como alcançada antes da execução dos experimentos.

## 8. Relação entre negócio e modelo

O projeto utilizará a seguinte lógica:

Problema de negócio → KPI financeiro → Objetivo analítico → Métricas técnicas → Modelo validado → Apoio à decisão de crédito.

Uma melhoria nas métricas técnicas não representa automaticamente redução real das perdas financeiras.

Esse impacto dependerá da política de concessão, dos custos envolvidos e de validação posterior em operação.

---

## 9. Referências

**Materiais da FIAP:**

- Capítulo 01 — Introdução ao CRISP-DM;
- Capítulo 02 — Problema de Negócio e Variável-Alvo;
- Capítulo 03 — Metas de Negócio vs. Metas Analíticas;
- Capítulo 04 — Dor de Negócio → Solução de Dados;
- Estatística Essencial — Aula 04: Testes de Hipótese.

**Arquivos do desafio:**

- `Desafio_Disciplina_PayFlow_Credit_Risk.docx`;
- `dicionario_dados_payflow.md`.