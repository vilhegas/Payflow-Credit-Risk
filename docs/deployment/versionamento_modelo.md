# Empacotamento e Versionamento — PayFlow Credit Risk

## 1. Objetivo

Preservar o pipeline treinado e sua configuração para permitir inferência reprodutível fora do notebook de modelagem.

## 2. Artefatos

| Arquivo | Finalidade |
|---|---|
| `models/modelo_payflow_v1.joblib` | Pipeline treinado de pré-processamento e Regressão Logística |
| `models/modelo_payflow_v1.json` | Metadados, features, threshold, versão e resultados |
| `notebooks/04_modelagem.ipynb` | Histórico experimental e avaliação do modelo |

## 3. Configuração selecionada

- Algoritmo: Regressão Logística
- Versão inicial: 1.0.0
- Threshold: 0,20
- Horizonte de previsão: 90 dias
- Quantidade de variáveis preditoras: 17

O threshold é preservado nos metadados e deverá ser aplicado às probabilidades retornadas por `predict_proba`.

## 4. Estratégia de versionamento

Alterações no algoritmo, nos dados de treinamento, no pré-processamento, no threshold ou na definição da variável-alvo deverão ser registradas e avaliadas antes da liberação de uma nova versão.

Cada versão aprovada deverá preservar a rastreabilidade entre o código-fonte, o treinamento, a avaliação e os artefatos utilizados na inferência.

## 5. Validação técnica

O processo de empacotamento prevê:

1. Serialização do pipeline treinado.
2. Persistência dos metadados.
3. Carregamento do artefato.
4. Comparação das probabilidades antes e depois da serialização.
5. Verificação do threshold registrado.

A aprovação desse teste comprova equivalência técnica de carregamento, não aptidão do modelo para produção.

## 6. Limitações e segurança

A compatibilidade entre versões do Scikit-learn deve ser controlada.

Artefatos serializados não confiáveis não devem ser carregados.

A implantação operacional exigiria controles adicionais de integridade, acesso, auditoria, disponibilidade e aprovação de negócio.

## 7. Referências

- FIAP — Introdução ao CRISP-DM, seção Deployment.
- Desafio da Disciplina — PayFlow Credit Risk.
- `docs/deployment/arquitetura.md`.
- `docs/deployment/contrato_api.md`.
- `docs/modeling/avaliacao_modelo.md`.