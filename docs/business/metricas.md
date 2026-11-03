# Metas de Negócio e Metas Analíticas

**Projeto:** Credit Risk — Score de Inadimplência  
**Metodologia:** CRISP-DM  
**Fase:** Business Understanding  
**Status:** Metas e critérios analíticos documentados; custos reais e critérios operacionais permanecem pendentes de dados da PayFlow

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

## 6.1 Justificativa do threshold 0,20

O threshold de 0,20 foi mantido como valor experimental da baseline histórica porque ele equilibra melhor precision e recall para o contexto do desafio, sem que os custos reais de falso positivo e falso negativo tenham sido fornecidos.

A escolha histórica foi feita principalmente pela análise do F1-score nas previsões out-of-fold do desenvolvimento, uma métrica que combina precision e recall. Esse critério é útil quando a classe positiva é minoritária, mas não incorpora custos financeiros ou operacionais.

Entretanto, o valor do threshold não representa uma política de crédito definitiva. Em cenários de crédito real, o custo de um falso negativo (conceder crédito a um cliente que se torna inadimplente) e o custo de um falso positivo (rejeitar um cliente que seria saudável) podem ser muito diferentes. Sem essas informações operacionais, não é possível afirmar que um threshold econômicomente ótimo exista ou que o melhor valor estatístico seja adequado ao negócio.

A análise deve, portanto, ser interpretada como uma simulação experimental de apoio à decisão, com 0,20 preservado como referência histórica e não como regra operacional formal.

## 6.2 Sensibilidade econômica simulada

As previsões utilizadas são OOF e provêm exclusivamente dos 4.000 registros de desenvolvimento. Foi usada a regressão logística histórica, com `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)`; cada pipeline ajusta as transformações somente no fold de treino. O teste de 1.000 registros não participou dessa análise. A execução reproduzível é `python -m src.experiments.development_validation`.

| Threshold | TP | TN | FP | FN | Precision | Recall | F1 |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0,10 | 358 | 2.370 | 1.143 | 129 | 0,2385 | 0,7351 | 0,3602 |
| 0,15 | 285 | 2.884 | 629 | 202 | 0,3118 | 0,5852 | 0,4069 |
| 0,20 | 229 | 3.118 | 395 | 258 | 0,3670 | 0,4702 | 0,4122 |
| 0,25 | 193 | 3.247 | 266 | 294 | 0,4205 | 0,3963 | 0,4080 |
| 0,30 | 162 | 3.335 | 178 | 325 | 0,4765 | 0,3326 | 0,3918 |
| 0,40 | 110 | 3.410 | 103 | 377 | 0,5164 | 0,2259 | 0,3143 |
| 0,50 | 77 | 3.453 | 60 | 410 | 0,5620 | 0,1581 | 0,2468 |

Para comparar cenários sem atribuir valores monetários inexistentes, cada erro recebe unidades relativas hipotéticas. O custo total é `FP × custo_FP + FN × custo_FN`.

| Threshold | FP=FN (1:1) | FN=3×FP (1:3) | FP=3×FN (3:1) | FN=5×FP (1:5) |
|---:|---:|---:|---:|---:|
| 0,10 | 1.272 | 1.530 | 3.558 | 1.788 |
| 0,15 | 831 | 1.235 | 2.089 | 1.639 |
| 0,20 | 653 | 1.169 | 1.443 | 1.685 |
| 0,25 | 560 | 1.148 | 1.092 | 1.736 |
| 0,30 | 503 | 1.153 | 859 | 1.803 |
| 0,40 | 480 | 1.234 | 686 | 1.988 |
| 0,50 | 470 | 1.290 | 590 | 2.110 |

O limiar menor identifica mais inadimplentes, mas também gera mais falsos positivos; no desenvolvimento, o recall cai de 0,7351 para 0,1581 ao passar de 0,10 a 0,50, enquanto FP cai de 1.143 para 60. Os limiares de menor custo variam conforme a relação hipotética: 0,50 em 1:1 e 3:1, 0,25 em 1:3, e 0,15 em 1:5. Isso ilustra que não há um threshold economicamente ótimo sem estimativas aprovadas de custo. As unidades não representam reais nem perdas financeiras da PayFlow; a simulação ignora exposição, severidade, recuperação, taxa de aprovação, efeitos comportamentais e incerteza das previsões. Não altera o threshold histórico de 0,20.

## 6.3 Comparação reproduzível das estratégias de imputação

As três estratégias usam a mesma divisão de desenvolvimento (4.000 registros), os mesmos cinco folds estratificados embaralhados (`random_state=42`), Regressão Logística (`max_iter=1000`, `random_state=42`) e os mesmos critérios. A imputação de grupo estima as medianas por `autonomo` dentro de cada fold, com mediana global daquele fold como fallback. Métricas de classificação usam threshold 0,20 sobre previsões OOF. O ambiente registrado foi Python 3.12, pandas 3.1.0, NumPy 2.5.4 e scikit-learn 1.9.1.

| Estratégia | ROC-AUC média (DP) | ROC-AUC OOF | Precision | Recall | F1 | Brier |
|---|---:|---:|---:|---:|---:|---:|
| Mediana global (baseline) | 0,776201 (0,033326) | 0,774315 | 0,366987 | 0,470226 | 0,412241 | 0,091124 |
| Mediana + indicadores de ausência | 0,775194 (0,032939) | 0,773545 | 0,372990 | 0,476386 | 0,418395 | 0,091318 |
| Mediana por grupo do tempo de emprego | 0,776274 (0,033252) | 0,774335 | 0,366987 | 0,470226 | 0,412241 | 0,091125 |

Diferenças em relação à mediana global: ROC-AUC média/OOF de `−0,001007/−0,000770` para indicadores e `+0,000073/+0,000020` para grupo; precision OOF `+0,006003` e recall OOF `+0,006160` para indicadores; F1 `+0,006154` e Brier `+0,000194` para indicadores. Para o grupo, precision, recall e F1 mudaram `0,000000`, e o Brier aumentou `0,000001`. O indicador apresenta uma troca pequena sem evidência suficiente para substituir a baseline. A imputação por grupo produz resultados praticamente iguais e não justifica complexidade adicional nesta base. Não se atribui significância estatística a diferenças que não foram submetidas a teste pareado ou intervalo de confiança.

As referências históricas de 0,7762 (média dos AUCs dos folds) e 0,7743 (AUC agregada das probabilidades OOF) foram reproduzidas. O valor 0,7652 não pôde ser vinculado a parâmetros, divisão ou versão registrados; permanece como resultado anterior não reproduzido, e não foi forçado a coincidir.

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

## Resultados obtidos — Avaliação final

Após a execução das etapas de modelagem e avaliação, foi selecionada a Regressão Logística, utilizando threshold de classificação de 0,20.

Os resultados no conjunto de teste reservado, composto por 1.000 registros, foram:

| Métrica | Resultado |
|---|---:|
| Acurácia | 82,70% |
| Precision | 33,76% |
| Recall | 43,44% |
| F1-score | 37,99% |
| ROC-AUC | 0,7202 |
| Brier Score | 0,0977 |

O modelo identificou corretamente 53 dos 122 clientes inadimplentes presentes no conjunto de teste.

Entretanto, 69 inadimplentes não foram identificados e 104 clientes adimplentes foram classificados como possíveis inadimplentes.

**Conclusão:** o modelo apresentou capacidade preditiva, mas suas limitações impedem afirmar que esteja pronto para decisões automáticas de concessão de crédito.

O impacto financeiro real não foi calculado, pois o dataset não disponibiliza os custos necessários para quantificar as consequências dos erros de classificação.

A avaliação experimental foi concluída. A validação de impacto de negócio permanece pendente de dados operacionais reais.

## Métricas complementares e ablações

As métricas da tabela abaixo foram calculadas com previsões OOF nos 4.000 registros de desenvolvimento, usando folds estratificados compartilhados (`random_state=42`). Precision, recall e F1 são mostrados no threshold 0,20; Average Precision usa probabilidades e `average_precision_score`, não integração trapezoidal da curva PR. A prevalência de default (0,12175) serve como referência aproximada para Average Precision.

| Experimento | ROC-AUC OOF | Average Precision | Precision | Recall | F1 | Brier | Brier Skill Score |
|---|---:|---:|---:|---:|---:|---:|---:|
| Regressão Logística original | 0,7743 | 0,3799 | 0,3670 | 0,4702 | 0,4122 | 0,0911 | 0,1478 |
| Random Forest | 0,7719 | 0,3907 | 0,3699 | 0,4990 | 0,4248 | 0,0916 | 0,1430 |
| Regressão Logística, `class_weight="balanced"` | 0,7726 | 0,3783 | 0,1421 | 0,9569 | 0,2474 | 0,1843 | -0,7238 |

O Brier Skill Score é `1 − Brier(modelo) / Brier(preditora constante)`. Para cada fold, a preditora constante usa apenas a prevalência do respectivo conjunto de treino; as probabilidades de referência OOF mantêm esse valor por observação. Um valor positivo indica menor erro quadrático que a referência; um valor negativo, maior erro. O peso balanceado elevou o recall, mas reduziu muito a precision e piorou a calibração; a baseline permaneceu inalterada.

O Random Forest apresentou F1 e Average Precision maiores no desenvolvimento, enquanto a Regressão Logística apresentou ROC-AUC e Brier ligeiramente melhores. A escolha acadêmica da Regressão Logística privilegia a interpretação mais direta, assumindo explicitamente F1 inferior no corte comparado. A diferença de AUC não prova equivalência ou superioridade estatística. A escolha dos modelos e threshold no mesmo desenvolvimento pode produzir otimismo.

| Ablação exploratória | ROC-AUC OOF | Average Precision OOF |
|---|---:|---:|
| Original | 0,7743 | 0,3799 |
| Sem `regiao` | 0,7760 | 0,3824 |
| Sem `regiao`, `idade` e `canal_aquisicao` | 0,7773 | 0,3828 |
| Incluindo `juros_mensal_pct` | 0,7753 | 0,3822 |

A correlação de Pearson entre juros e score de crédito foi -0,8007 nos dados de desenvolvimento. O valor é descritivo; não demonstra a sequência operacional nem causalidade. Como não foi comprovado que a taxa está disponível antes da decisão, sua exclusão da baseline permanece. Remover features por pequenas diferenças destas ablações não garante redução de vieses.

## Intervalos de confiança históricos

Bootstrap pareado por cliente, 5.000 reamostragens com semente 42, intervalo percentil de 95%. Reamostragens sem classes suficientes são descartadas; neste cálculo, nenhuma foi descartada.

| Métrica do teste histórico | Estimativa | IC 95% |
|---|---:|---:|
| ROC-AUC | 0,7202 | 0,6665–0,7726 |
| Precision em threshold 0,20 | 0,3376 | 0,2642–0,4140 |
| Recall em threshold 0,20 | 0,4344 | 0,3475–0,5254 |

O teste já foi consultado e estes intervalos apenas quantificam a incerteza dessa avaliação. Eles não são nova validação independente nem foram usados em seleção. CSVs e JSONs com precisão integral ficam em `reports/experiments/`; consulte `docs/auditoria/decisoes_limitacoes.md` para resultados de leakage e métricas exploratórias por grupo.
