# Avaliação do Modelo — PayFlow Credit Risk

## 1. Objetivo

Avaliar a capacidade de um modelo de Regressão Logística de prever inadimplência em até 90 dias, considerando desempenho preditivo, identificação de clientes inadimplentes e qualidade das probabilidades estimadas.

## 2. Modelo selecionado

- **Algoritmo:** Regressão Logística
- **Threshold:** 0,20
- **Dados de treinamento:** 4.000 registros
- **Dados de teste:** 1.000 registros
- **Validação:** Stratified K-Fold com cinco divisões

O F1 OOF no threshold 0,20 foi a métrica prioritária para comparar a identificação da classe positiva minoritária; a ROC-AUC avaliou a discriminação. No desenvolvimento, a Regressão Logística obteve F1 OOF de 0,4122 e ROC-AUC média por fold de 0,7762. A Random Forest obteve F1 OOF de 0,4248 e ROC-AUC média de 0,7727: vantagem de F1 de 0,0126 para a floresta e diferença de ROC-AUC de 0,0035 a favor da regressão. A escolha final não foi determinada pelo maior F1 isoladamente: a Regressão Logística foi mantida como referência acadêmica por sua interpretação mais direta, aceitando explicitamente o F1 um pouco menor. Essa decisão reflete o objetivo pedagógico de um modelo interpretável, não uma superioridade preditiva ou operacional.

O limiar 0,20 foi mantido como baseline histórica e não foi substituído pelo menor custo hipotético. O limiar e os modelos foram comparados na mesma validação cruzada; selecionar a combinação com melhor resultado nesses dados pode produzir otimismo de seleção. Uma avaliação confirmatória exigiria validação aninhada ou novos dados de desenvolvimento. O teste histórico permanece reservado para avaliação final já realizada e não foi usado nesses experimentos.

## 3. Resultados finais

| Métrica | Resultado |
|---|---:|
| Acurácia | 82,70% |
| Precision | 33,76% |
| Recall | 43,44% |
| F1-score | 37,99% |
| ROC-AUC | 0,7202 |
| Brier Score | 0,0977 |

## 4. Matriz de confusão

| Classificação | Clientes |
|---|---:|
| Verdadeiros negativos | 774 |
| Falsos positivos | 104 |
| Falsos negativos | 69 |
| Verdadeiros positivos | 53 |

O modelo identificou 53 dos 122 clientes inadimplentes no conjunto de teste, deixando de identificar outros 69.

## 5. Calibração

O Brier Score foi de 0,0911 na validação cruzada e 0,0977 no teste final.

A curva de calibração da validação cruzada apresentou proximidade visual com a linha ideal nas faixas observadas. Esse resultado é favorável, embora não garanta calibração adequada em todos os segmentos e faixas de risco.

## 6. Limitações

- O dataset utilizado é sintético.
- Os custos financeiros de falsos positivos e falsos negativos não foram fornecidos.
- O modelo apresenta recall limitado.
- Não foi possível realizar validação temporal por ausência de datas de concessão.
- A definição operacional exata de default depende de confirmação.
- A disponibilidade de todas as variáveis no momento da decisão precisa ser verificada em produção.
- Não houve otimização sistemática de hiperparâmetros.
- O threshold 0,20 foi preservado como referência histórica após comparação discreta de valores de F1 OOF; a análise econômica hipotética não o substituiu. A seleção de modelos e thresholds nos mesmos folds pode gerar otimismo, e uma confirmação exigiria validação aninhada ou nova amostra de desenvolvimento.
- O Random Forest apresentou F1-score ligeiramente maior na comparação exploratória, mas a Regressão Logística foi priorizada pela interpretabilidade e pelo ROC-AUC.
- A diferença entre os experimentos anteriores que citavam ROC-AUC média 0,7762 e OOF 0,7743 foi reproduzida porque são agregações distintas dos mesmos folds. A referência 0,7652 não pôde ser associada a uma configuração registrada e permanece sem reprodução.

## 7. Decisão

A Regressão Logística com threshold de 0,20 será mantida como **modelo de referência para a proposta acadêmica de implantação**.

Seu desempenho não justifica, isoladamente, a automação de decisões de concessão de crédito. Uma utilização operacional exigiria validação adicional, análise de custos, políticas de decisão, monitoramento e governança.

O conjunto de teste reservado já foi utilizado na avaliação final. Alterações futuras no modelo deverão ser avaliadas por um novo protocolo de validação, sem reutilizar esse teste para selecionar configurações.

## 8. Métricas complementares

Na validação OOF de desenvolvimento, a Average Precision foi 0,3799 para Regressão Logística e 0,3907 para Random Forest, ante prevalência 0,12175. Foi calculada por `average_precision_score`, que não é a integração trapezoidal da curva precision-recall. O Brier Skill Score foi 0,1478 e 0,1430, respectivamente, em relação à prevalência de treino específica de cada fold. A análise de `class_weight="balanced"` aumentou recall, mas reduziu precision e piorou Brier; não alterou a baseline.

Os intervalos de ROC-AUC, precision e recall do teste histórico constam em `docs/auditoria/decisoes_limitacoes.md` e `reports/experiments/intervalos_teste_historico.json`. Como o teste já havia sido consultado, os intervalos somente quantificam incerteza amostral; não contam como nova validação.

## 9. Referências

- FIAP — Introdução ao CRISP-DM.
- FIAP — Metas de Negócio vs. Metas Analíticas.
- Desafio da Disciplina — PayFlow Credit Risk.
- `notebooks/04_modelagem.ipynb`.
