# PayFlow Credit Risk — Previsão de Inadimplência

Projeto acadêmico da **FIAP Pós-Tech — AI Scientist**, desenvolvido com a metodologia **CRISP-DM** para estimar a probabilidade de inadimplência de clientes nos **90 dias após a concessão de crédito**. A PayFlow é uma fintech fictícia que oferece empréstimos pessoais, cartões e BNPL.

## Objetivo

Desenvolver e avaliar um modelo de classificação binária (`default_90d`), identificar riscos de *data leakage* e propor sua disponibilização por API REST, com monitoramento e governança. **O modelo é uma demonstração acadêmica e não deve ser usado isoladamente para aprovar ou negar crédito.**

## Dados e metodologia

- **Base:** 5.000 clientes e 23 colunas, em dataset sintético.
- **Preparação:** seleção de 17 variáveis preditoras, imputação de ausentes, padronização numérica e One-Hot Encoding; exclusão de identificador, alvo e variáveis com informações futuras.
- **Validação:** divisão estratificada de 80% para treinamento e 20% para teste; validação cruzada estratificada com 5 divisões no treinamento.
- **Modelos comparados:** Dummy Classifier, Regressão Logística, Árvore de Decisão e Random Forest.
- **Modelo de referência acadêmica:** Regressão Logística com threshold histórico **0,20**. Na validação OOF, a Random Forest obteve F1 0,4248 contra 0,4122 da regressão; a Regressão Logística foi mantida por interpretabilidade e diferença pequena de ROC-AUC (0,7762 contra 0,7727), não por maior F1.

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
reports/experiments/   # Resultados versionados e configurações dos experimentos
src/experiments/       # Scripts reprodutíveis de análise em desenvolvimento
tests/                 # Testes unitários e do artefato histórico
```

## Como executar

No terminal PowerShell, na raiz do projeto:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
jupyter lab
```

Execute os notebooks, em ordem: `01_auditoria.ipynb`, `02_eda.ipynb`, `03_preparacao.ipynb` e `04_modelagem.ipynb`. Se usar VS Code, selecione o interpretador Python do `.venv` como kernel.

Para reproduzir as comparações de imputação e sensibilidade do threshold sem usar o conjunto de teste para seleção, execute na raiz do repositório:

```powershell
python -m src.experiments.development_validation
python -m src.experiments.complementary_analysis
python -m src.models.reproduce_v1 --output-dir reports/reproduced_v1
python -m pytest -q -p no:cacheprovider
```

Os experimentos de comparação usam somente os 4.000 registros de desenvolvimento. A análise complementar inclui Average Precision, Brier Skill Score com prevalência de treino por fold, class weight, ablações de features, demonstração separada de leakage e análise exploratória por grupos. O bootstrap do teste histórico serve apenas para quantificar incerteza de uma avaliação já consultada, sem uso para seleção. Sementes, parâmetros, versões e resultados ficam em `reports/experiments/`.

O comando de reprodução do modelo escreve em uma pasta indicada pelo usuário e se recusa a sobrescrever artefatos existentes. Os testes também treinam uma cópia temporária e comparam suas probabilidades e metadados com a v1 versionada.

> **Artefato do modelo:** `models/modelo_payflow_v1.joblib` e seu JSON são versionados como baseline acadêmica; os testes conferem o carregamento, a versão do scikit-learn, o schema e as métricas históricas. A célula final do notebook reproduz e compara os metadados sem sobrescrever o artefato original. Arquivos Joblib devem ser carregados somente de fontes confiáveis.

Para instalar o ambiente de notebooks sem ferramentas de teste, use `python -m pip install -r requirements.txt`. O projeto foi executado com Python 3.12; versões de bibliotecas estão fixadas nos arquivos de dependências. Em um clone limpo, valide a instalação e rode `python -m pytest -q -p no:cacheprovider`.

## Proposta de implantação

A documentação especifica uma **proposta acadêmica de API REST**, com `POST /api/v1/predict` para receber as 17 variáveis e devolver probabilidade, classificação e versão do modelo, e `GET /health` para indicar a disponibilidade do serviço e do artefato. A camada da API validaria campos e categorias antes da inferência; categorias fora do vocabulário observado no CSV seriam rejeitadas com HTTP 422, embora o `OneHotEncoder` configurado possa ignorá-las tecnicamente. O contrato também propõe autenticação/autorização, HTTPS, restrição de acesso e versionamento do caminho. Esses endpoints e o monitoramento de drift, logs e retreinamento são **propostos, não implementados nem implantados**. As categorias documentadas são as encontradas no CSV atual; seu alinhamento com sistemas operacionais precisaria ser confirmado antes de uma implantação.

## Limitações

A base é sintética, não possui datas para validação temporal e não especifica integralmente a regra operacional de default nem a origem e o momento real de disponibilidade das variáveis. O split aleatório pode misturar safras que uma avaliação temporal manteria separadas. Os custos financeiros de falsos positivos e falsos negativos não foram fornecidos. Portanto, o threshold escolhido é uma decisão técnica experimental, não uma política operacional de concessão de crédito. A análise por grupos é exploratória e não demonstra fairness nem adequação para decisões reais.

## Referências

Materiais didáticos da **FIAP Pós-Tech — AI Scientist**, enunciado *Desafio da Disciplina — CRISP-DM na Prática* e dicionário de dados PayFlow disponíveis em `docs/desafio/`.
