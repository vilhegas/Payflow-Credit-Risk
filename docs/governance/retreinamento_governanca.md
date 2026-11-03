# Plano de Retreinamento e Governança — PayFlow Credit Risk

## 1. Objetivo

Estabelecer critérios e procedimentos para acompanhar, atualizar e controlar as versões do modelo de previsão de inadimplência da PayFlow.

O objetivo é garantir que possíveis alterações sejam justificadas, avaliadas, documentadas e aprovadas antes de sua utilização operacional.

Este documento descreve uma proposta acadêmica de MLOps. Os procedimentos ainda não foram implementados em produção.

## 2. Modelo de referência

| Característica | Configuração |
|---|---|
| Versão inicial | 1.0.0 |
| Algoritmo | Regressão Logística |
| Threshold | 0,20 |
| Target | `default_90d` |
| Horizonte de previsão | 90 dias |
| ROC-AUC de teste | 0,7202 |
| Recall de teste | 43,44% |
| F1-score de teste | 37,99% |
| Brier Score de teste | 0,0977 |

Os resultados são referências acadêmicas obtidas com dados sintéticos, não metas mínimas de produção.

## 3. Critérios para investigar retreinamento

O retreinamento poderá ser considerado quando forem identificadas mudanças relevantes, como:

- **Data Drift:** alterações persistentes na distribuição das variáveis utilizadas pelo modelo.
- **Prediction Drift:** mudanças importantes na distribuição das probabilidades estimadas.
- **Degradação de desempenho:** redução relevante de métricas como recall, ROC-AUC ou F1-score, calculadas com resultados reais consolidados.
- **Problemas de calibração:** divergências persistentes entre probabilidades previstas e frequências observadas.
- **Mudanças no negócio:** novos produtos, alterações na política de crédito ou mudanças significativas no perfil dos clientes.
- **Mudanças na definição do target:** revisão formal do evento considerado inadimplência.

Um alerta não deverá provocar retreinamento automático. Primeiro, será necessário investigar sua causa e verificar se o problema decorre de mudança nos dados, falha operacional ou alteração real do comportamento de risco.

## 4. Frequência de avaliação

Propõe-se uma revisão trimestral da necessidade de retreinamento, além de avaliações extraordinárias motivadas por alertas relevantes.

Essa frequência é uma proposta inicial e deverá ser ajustada conforme volume de operações, disponibilidade dos resultados e necessidades da PayFlow.

O acompanhamento de desempenho dependerá de observações cujo horizonte de 90 dias esteja completo e cujo resultado tenha sido consolidado.

## 5. Processo proposto de retreinamento

O processo seguirá as seguintes etapas:

1. Registrar o motivo da revisão do modelo.
2. Verificar qualidade, integridade e disponibilidade temporal das novas informações.
3. Confirmar a definição vigente da variável-alvo.
4. Construir uma base de treinamento com resultados consolidados.
5. Realizar as divisões de treinamento, validação e teste apropriadas ao contexto temporal.
6. Reajustar o pipeline de pré-processamento utilizando somente os dados de treinamento.
7. Treinar modelos candidatos e executar validação.
8. Avaliar discriminação, recall, precision, calibração e custos de erro.
9. Comparar o modelo candidato com a versão vigente em condições equivalentes.
10. Documentar resultados e obter as aprovações necessárias.
11. Implantar de forma controlada, quando autorizado.
12. Monitorar o comportamento da nova versão e manter um procedimento de reversão.

O conjunto de teste utilizado na avaliação acadêmica da versão 1.0.0 não deverá ser reutilizado repetidamente para selecionar novas configurações.

## 6. Critérios para aprovação de uma nova versão

Uma versão candidata somente poderá substituir a anterior depois de atender aos critérios aprovados pelas áreas responsáveis.

A avaliação deverá considerar:

- Qualidade e consistência dos dados.
- Desempenho em dados não utilizados no treinamento ou seleção.
- Robustez temporal e por segmentos relevantes.
- Calibração das probabilidades.
- Custos de falsos positivos e falsos negativos.
- Interpretabilidade e documentação.
- Reprodutibilidade das transformações e previsões.
- Compatibilidade com o contrato da API.
- Segurança, privacidade e rastreabilidade.

Não serão definidos limites numéricos de aprovação neste momento, porque o desafio não fornece metas operacionais nem custos de decisão.

Antes de qualquer uso real, a PayFlow deverá formalizar esses critérios.

## 7. Governança da variável-alvo

A variável `default_90d` representa o resultado de inadimplência observado no horizonte de 90 dias.

Entretanto, o material fornecido não estabelece a regra operacional exata para caracterizar o evento.

Portanto, antes de uma implantação real, será necessário definir e documentar:

- Evento que caracteriza default.
- Data de início do período de observação.
- Critérios de elegibilidade das operações.
- Tratamento de contratos cancelados ou sem observação completa.
- Fonte oficial de identificação do evento.
- Regras para correções e atualizações dos registros.

Não se deve interpretar automaticamente `default_90d` como atraso superior a 90 dias. O horizonte de observação e a duração do atraso são conceitos diferentes.

A definição formal deverá possuir versão própria, e mudanças posteriores deverão ser avaliadas quanto à compatibilidade histórica.

## 8. Versionamento e rastreabilidade

Cada versão deverá possuir registros que permitam identificar:

| Elemento | Informação registrada |
|---|---|
| Modelo | Algoritmo e versão |
| Pré-processamento | Transformações e configurações |
| Dados | Origem, período e versão do conjunto |
| Target | Definição e versão da regra |
| Features | Lista, tipos e disponibilidade temporal |
| Threshold | Valor utilizado e justificativa |
| Avaliação | Métricas, limitações e critérios |
| Código | Identificador do commit |
| Artefato | Identificador e verificação de integridade |
| Aprovação | Responsável e registro da decisão |

O artefato serializado e seus metadados deverão ser preservados de forma segura e recuperável.

## 9. Estratégia de implantação controlada

Uma eventual substituição do modelo poderá ser realizada inicialmente em modo de observação (*shadow mode*), no qual a versão candidata gera previsões sem interferir nas decisões de crédito.

Após avaliação e aprovação, a utilização poderá ser ampliada gradualmente.

A organização deverá preservar a possibilidade de retornar à versão anterior em caso de falhas ou degradação relevante.

A troca do modelo não deverá ocorrer automaticamente apenas porque uma nova versão apresenta resultado superior em uma única métrica.

## 10. Governança das decisões de crédito

O modelo estima a probabilidade de inadimplência, mas não determina sozinho a decisão de concessão.

A política de decisão deverá considerar fatores de negócio, custos, regras aplicáveis e processos de revisão.

Também será necessário avaliar possíveis diferenças de desempenho e impacto entre segmentos de clientes, evitando que uma métrica agregada oculte problemas importantes.

## 11. Responsabilidades

| Área | Responsabilidade proposta |
|---|---|
| Ciência de Dados | Treinamento, validação e documentação |
| Engenharia/MLOps | Implantação, versionamento técnico e monitoramento |
| Risco de Crédito | Critérios de negócio e política de decisão |
| Governança/Compliance | Controles, rastreabilidade e conformidade |
| Responsáveis pela aprovação | Autorizar ou rejeitar a substituição do modelo |

## 12. Limitações

O projeto utiliza dados sintéticos e não dispõe de histórico temporal adequado para simular integralmente o processo de atualização.

Os custos financeiros dos erros ainda não foram definidos.

A definição operacional de inadimplência precisa ser formalizada.

A comparação entre versões futuras dependerá de novos dados, critérios aprovados e avaliação independente.

Assim, este plano representa uma estratégia de governança proposta, não um processo operacional já implantado.

## 13. Referências

- FIAP — Introdução ao CRISP-DM.
- FIAP — Problema de Negócio e Variável-Alvo.
- FIAP — Metas de Negócio vs. Metas Analíticas.
- Desafio da Disciplina — PayFlow Credit Risk.
- `docs/deployment/monitoramento_mlops.md`.
- `docs/deployment/versionamento_modelo.md`.
- `docs/modeling/avaliacao_modelo.md`.