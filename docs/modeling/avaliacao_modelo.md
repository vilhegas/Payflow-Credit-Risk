# Avaliação do Modelo — PayFlow Credit Risk

## 1. Objetivo

Avaliar a capacidade de um modelo de Regressão Logística de prever inadimplência em até 90 dias, considerando desempenho preditivo, identificação de clientes inadimplentes e qualidade das probabilidades estimadas.

## 2. Modelo selecionado

- **Algoritmo:** Regressão Logística
- **Threshold:** 0,20
- **Dados de treinamento:** 4.000 registros
- **Dados de teste:** 1.000 registros
- **Validação:** Stratified K-Fold com cinco divisões

A seleção considerou interpretabilidade, ROC-AUC e equilíbrio entre precision e recall. O threshold foi escolhido com base no F1-score observado na validação cruzada.

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
- A escolha do threshold foi baseada em uma comparação discreta de valores, com possível otimismo de seleção.
- O Random Forest apresentou F1-score ligeiramente maior na comparação exploratória, mas a Regressão Logística foi priorizada pela interpretabilidade e pelo ROC-AUC.

## 7. Decisão

A Regressão Logística com threshold de 0,20 será mantida como **modelo de referência para a proposta acadêmica de implantação**.

Seu desempenho não justifica, isoladamente, a automação de decisões de concessão de crédito. Uma utilização operacional exigiria validação adicional, análise de custos, políticas de decisão, monitoramento e governança.

O conjunto de teste reservado já foi utilizado na avaliação final. Alterações futuras no modelo deverão ser avaliadas por um novo protocolo de validação, sem reutilizar esse teste para selecionar configurações.

## 8. Referências

- FIAP — Introdução ao CRISP-DM.
- FIAP — Metas de Negócio vs. Metas Analíticas.
- Desafio da Disciplina — PayFlow Credit Risk.
- `notebooks/04_modelagem.ipynb`.