# Plano de Monitoramento e MLOps — PayFlow Credit Risk

## 1. Objetivo

Definir uma estratégia de acompanhamento contínuo do modelo de previsão de inadimplência da PayFlow após sua eventual disponibilização como serviço de inferência.

O monitoramento deverá permitir identificar mudanças nos dados, alterações nas previsões, degradação de desempenho e problemas operacionais.

Este documento apresenta uma proposta acadêmica. Os controles descritos ainda não estão implementados em produção.

## 2. Modelo monitorado

| Característica | Configuração |
|---|---|
| Algoritmo | Regressão Logística |
| Versão inicial | 1.0.0 |
| Threshold | 0,20 |
| Variável-alvo | `default_90d` |
| Horizonte de previsão | 90 dias |
| ROC-AUC de referência | 0,7202 |
| Recall de referência | 43,44% |
| F1-score de referência | 37,99% |
| Brier Score de referência | 0,0977 |

Os valores de referência correspondem à avaliação no conjunto de teste sintético. Não representam metas operacionais aprovadas pela PayFlow.

## 3. Monitoramento de Data Drift

Data Drift é a alteração da distribuição das variáveis de entrada em relação aos dados utilizados no desenvolvimento do modelo.

Serão acompanhadas variáveis como:

- `score_credito`: distribuição dos scores dos novos clientes.
- `renda_mensal`: mudanças na distribuição de renda e percentual de valores ausentes.
- `valor_solicitado`: alterações nos valores solicitados.
- `utilizacao_credito`: mudanças no percentual de utilização.
- `tipo_produto`: mudanças na participação dos produtos de crédito.
- `canal_aquisicao`: mudanças no perfil dos canais de entrada.

### Estratégia proposta

Comparar periodicamente os dados recebidos com uma distribuição de referência definida a partir dos dados de desenvolvimento.

Poderão ser utilizados indicadores estatísticos como PSI, KS e medidas de distância entre distribuições, conforme o tipo de variável.

A interpretação deverá considerar tamanho amostral, relevância da mudança e impacto potencial sobre as previsões.

Alertas não deverão provocar retreinamento automático sem investigação.

## 4. Monitoramento de Prediction Drift

Prediction Drift ocorre quando a distribuição das probabilidades estimadas pelo modelo se modifica ao longo do tempo.

Indicadores propostos:

- Probabilidade média prevista.
- Distribuição das probabilidades de default.
- Percentual de clientes com classificação 1.
- Proporção de clientes por faixa de risco.

Esses indicadores poderão ser acompanhados mesmo antes da disponibilidade dos resultados reais de inadimplência.

Uma mudança nas previsões não demonstra, isoladamente, degradação do modelo. Ela deverá ser investigada juntamente com mudanças nos dados e no contexto de negócio.

## 5. Monitoramento de desempenho

Quando os resultados reais de `default_90d` estiverem disponíveis e consolidados, será possível calcular:

| Métrica | Finalidade |
|---|---|
| Recall | Avaliar identificação dos inadimplentes |
| Precision | Avaliar a proporção de alertas corretos |
| F1-score | Combinar precision e recall |
| ROC-AUC | Avaliar capacidade de discriminação |
| Brier Score | Avaliar erro das probabilidades |
| Matriz de confusão | Quantificar falsos positivos e falsos negativos |

As métricas deverão ser comparadas às referências históricas, com atenção ao tamanho das amostras e à incerteza estatística.

### Atraso na obtenção do target

A previsão é realizada no momento da solicitação de crédito, mas a avaliação de inadimplência depende do horizonte de 90 dias.

Por isso, a avaliação de desempenho deverá utilizar somente contratos ou observações cujo período de acompanhamento esteja completo e cujo resultado tenha sido consolidado.

Não deverão ser tratados como adimplentes clientes cujo horizonte de observação ainda não terminou.

## 6. Logging e rastreabilidade

Cada inferência deverá produzir um registro técnico contendo, quando aplicável:

- Identificador técnico da requisição.
- Data e horário da inferência.
- Versão do modelo.
- Versão do contrato da API.
- Probabilidade prevista.
- Threshold aplicado.
- Classificação produzida.
- Status da execução.
- Tempo de resposta.
- Identificador de referência dos dados, quando necessário e autorizado.

Os logs deverão seguir princípios de minimização de dados e controle de acesso, evitando exposição desnecessária de informações pessoais.

## 7. Monitoramento operacional da API

Serão acompanhados:

- Disponibilidade do serviço.
- Taxa de erros HTTP.
- Tempo de resposta.
- Volume de inferências.
- Falhas de validação dos dados.
- Falhas de carregamento do modelo.

Problemas operacionais deverão gerar alertas para a equipe responsável.

## 8. Frequência de acompanhamento

Frequências iniciais propostas, sujeitas à validação operacional:

| Monitoramento | Frequência proposta |
|---|---|
| Disponibilidade e erros da API | Contínua |
| Distribuição das previsões | Diária |
| Qualidade e drift dos dados | Semanal |
| Desempenho preditivo | Mensal, por safras com target consolidado |
| Revisão geral do modelo | Trimestral ou por evento relevante |

Essas frequências são sugestões de projeto, não exigências definidas no enunciado.

## 9. Gestão de alertas

Um alerta deverá iniciar uma investigação técnica e de negócio.

O processo proposto é:

1. Identificar a métrica alterada.
2. Verificar a qualidade e a integridade dos dados.
3. Investigar alterações no perfil dos clientes, produtos ou políticas de crédito.
4. Avaliar o impacto sobre as previsões.
5. Quando houver rótulos consolidados, verificar a mudança nas métricas de desempenho.
6. Registrar a investigação e decidir se são necessárias ações corretivas.

Possíveis ações incluem correção de fontes de dados, revisão das integrações, análise de recalibração ou estudo de retreinamento.

## 10. Responsabilidades

A operação deverá envolver responsabilidades definidas entre:

- **Ciência de Dados:** desempenho, calibração, drift e análise de retreinamento.
- **Engenharia e MLOps:** disponibilidade, implantação, logs e infraestrutura.
- **Risco de Crédito:** impacto de negócio e políticas de decisão.
- **Governança e Compliance:** rastreabilidade, conformidade e revisão de controles.

## 11. Limitações

O projeto utiliza dados sintéticos e não dispõe de uma operação real para medir drift em produção.

Os valores de referência resultam de uma avaliação acadêmica.

Antes de uma implantação real, será necessário estabelecer critérios objetivos de alerta, responsáveis, metas operacionais e procedimentos de resposta aprovados pela PayFlow.

## 12. Referências

- FIAP — Introdução ao CRISP-DM, seção Deployment.
- FIAP — Metas de Negócio vs. Metas Analíticas.
- FIAP — Problema de Negócio e Variável-Alvo.
- Desafio da Disciplina — PayFlow Credit Risk.
- `docs/modeling/avaliacao_modelo.md`.
- `docs/deployment/arquitetura.md`.
- `docs/deployment/contrato_api.md`.