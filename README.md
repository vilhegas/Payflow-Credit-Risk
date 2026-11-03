# PayFlow Credit Risk — Previsão de Inadimplência

Projeto acadêmico da **FIAP Pós-Tech — AI Scientist**, desenvolvido com a metodologia **CRISP-DM** para estimar a probabilidade de inadimplência de clientes nos **90 dias após a concessão de crédito**. A PayFlow é uma fintech fictícia que oferece empréstimos pessoais, cartões e BNPL.

## Objetivo

Desenvolver e avaliar um modelo de classificação binária (`default_90d`), identificar riscos de *data leakage* e propor sua disponibilização por API REST, com monitoramento e governança. **O modelo é uma demonstração acadêmica e não deve ser usado isoladamente para aprovar ou negar crédito.**

## Dados e metodologia

- **Base:** 5.000 clientes e 23 colunas, em dataset sintético.
- **Preparação:** seleção de 17 variáveis preditoras, imputação de ausentes, padronização numérica e One-Hot Encoding; exclusão de identificador, alvo e variáveis com informações futuras.
- **Validação:** divisão estratificada de 80% para treinamento e 20% para teste; validação cruzada estratificada com 5 divisões no treinamento.
- **Modelos comparados:** Dummy Classifier, Regressão Logística, Árvore de Decisão e Random Forest.
- **Modelo selecionado:** Regressão Logística com threshold **0,20**, considerando interpretabilidade, discriminação e equilíbrio entre precision e recall.

## Resultados no conjunto de teste

| Métrica | Resultado |
|---|---:|
| Acurácia | 82,70% |
| Precision | 33,76% |
| Recall | 43,44% |
| F1-score | 37,99% |
| ROC-AUC | 0,7202 |
| Brier Score | 0,0977 |

A matriz de confusão registrou **53 verdadeiros positivos, 69 falsos negativos, 104 falsos positivos e 774 verdadeiros negativos**. O desempenho evidencia utilidade experimental, mas também limitações importantes para uma operação de crédito.

## Estrutura do projeto

```text
data/raw/              # Dataset original
notebooks/             # 01_auditoria, 02_eda, 03_preparacao, 04_modelagem
src/features/          # Função reutilizável de pré-processamento
models/                # Artefatos serializados e metadados (gerados localmente)
docs/business/         # Problema e métricas de negócio
docs/data/             # EDA e preparação
docs/modeling/         # Avaliação do modelo
docs/deployment/       # Arquitetura REST, contrato, versionamento e MLOps
docs/governance/       # Retreinamento e governança
docs/auditoria/        # Diagnóstico inicial, checklist de correção e registro de evidências
reports/final/         # Relatório final para entrega acadêmica
```

## Como executar

No terminal PowerShell, na raiz do projeto:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
jupyter lab
```

Execute os notebooks, em ordem: `01_auditoria.ipynb`, `02_eda.ipynb`, `03_preparacao.ipynb` e `04_modelagem.ipynb`. Se usar VS Code, selecione o interpretador Python do `.venv` como kernel.

> **Artefato do modelo:** o `.gitignore` exclui os arquivos em `models/` do versionamento padrão. O arquivo `.joblib` pode ser regenerado ao executar o notebook de modelagem. Arquivos Joblib devem ser carregados somente de fontes confiáveis.

## Proposta de implantação

A documentação descreve uma **API REST de inferência** que recebe as 17 variáveis, aplica o pipeline e devolve uma probabilidade de default e uma classificação. Também apresenta estratégia de monitoramento de drift, métricas, logs, retreinamento e versionamento do target. **A API e o monitoramento não foram implantados em produção.**

## Limitações

A base é sintética, não possui datas para validação temporal e não especifica integralmente a regra operacional de default. Os custos financeiros de falsos positivos e falsos negativos não foram fornecidos. Portanto, o threshold escolhido é uma decisão técnica experimental, não uma política operacional de concessão de crédito.

## Referências

Materiais didáticos da **FIAP Pós-Tech — AI Scientist**, enunciado *Desafio da Disciplina — CRISP-DM na Prática* e dicionário de dados PayFlow disponíveis em `docs/desafio/`.
