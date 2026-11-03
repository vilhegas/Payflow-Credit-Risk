# Arquitetura de Deployment — PayFlow Credit Risk

## 1. Objetivo

Propor a disponibilização futura do modelo de previsão de inadimplência em 90 dias por meio de um serviço de inferência acessível através de API REST. O projeto não implementa nem implanta esse serviço.

A solução deverá permitir que sistemas internos da PayFlow consultem a probabilidade estimada de inadimplência de um cliente no momento da solicitação de crédito.

## 2. Modelo selecionado

| Componente | Configuração |
|---|---|
| Algoritmo | Regressão Logística |
| Threshold de classificação | 0,20 |
| Pré-processamento | Pipeline Scikit-learn |
| Variável-alvo | `default_90d` |
| Horizonte de previsão | 90 dias |
| ROC-AUC no teste | 0,7202 |
| Recall no teste | 43,44% |
| Brier Score no teste | 0,0977 |

O modelo foi validado experimentalmente com dados sintéticos. Sua utilização operacional exigiria avaliações adicionais.

## 3. Arquitetura proposta

A solução será composta pelos seguintes elementos:

1. **Sistema solicitante:** sistema interno de concessão de crédito da PayFlow.
2. **API REST:** interface responsável pelo recebimento e validação dos dados de entrada.
3. **Pipeline de pré-processamento:** transformação das variáveis conforme as regras utilizadas durante o treinamento.
4. **Modelo preditivo:** Regressão Logística responsável pela estimativa de inadimplência.
5. **Sistema de decisão:** componente responsável pela aplicação das políticas de crédito.
6. **Monitoramento:** registro das inferências, acompanhamento da qualidade dos dados e avaliação contínua do modelo.

## 4. Fluxo de inferência

O sistema de crédito envia os dados do cliente à API.

A API valida os campos recebidos e verifica se as informações necessárias estão disponíveis.

Os dados são processados pelo mesmo pipeline utilizado no treinamento.

A Regressão Logística calcula a probabilidade estimada de inadimplência.

A rota proposta `POST /api/v1/predict` retorna a probabilidade, a classificação obtida com threshold de 0,20 e a versão do modelo. A rota proposta `GET /health` informa disponibilidade do serviço e carregamento do artefato, sem receber dados de clientes.

O sistema de decisão utiliza essas informações em conjunto com regras de negócio e, quando necessário, revisão humana.

## 5. Prevenção de Data Leakage

A API deverá aceitar somente as 17 variáveis preditoras selecionadas durante a preparação.

Não deverão ser utilizadas como preditoras:

- `id_cliente`;
- `default_90d`;
- `parcelas_pagas_ate_3m`;
- `atraso_primeira_parcela_dias`;
- `status_apos_90d`;
- `juros_mensal_pct`.

O identificador do cliente poderá existir separadamente como metadado de rastreabilidade, desde que não seja utilizado pelo modelo.

A disponibilidade temporal das demais variáveis deverá ser confirmada antes de qualquer implantação real.

A validação do vocabulário categórico é responsabilidade da camada da API, antes da inferência. Com base no CSV atual, os valores conhecidos são `canal_aquisicao` (`app`, `loja`, `parceiro`, `site`), `regiao` (`Centro-Oeste`, `Nordeste`, `Norte`, `Sudeste`, `Sul`) e `tipo_produto` (`bnpl`, `cartao`, `emprestimo_pessoal`). Categorias desconhecidas devem ser rejeitadas com HTTP 422, ainda que o `OneHotEncoder(handle_unknown="ignore")` possa processá-las sem erro. O contrato detalhado está em `contrato_api.md`.

## 6. Tecnologias propostas

| Tecnologia | Finalidade |
|---|---|
| Python | Implementação do serviço |
| FastAPI | Disponibilização da API REST |
| Scikit-learn | Pré-processamento e inferência |
| Pydantic | Validação de entradas e saídas |
| Joblib | Serialização do pipeline treinado |
| Git/GitHub | Versionamento de código e documentação |

Essas ferramentas são propostas de implementação, não tecnologias obrigatórias estabelecidas pelo enunciado.

## 7. Segurança e rastreabilidade

A proposta deverá considerar autenticação e autorização dos sistemas consumidores, proteção de dados pessoais, restrição de acesso por identidade e regras de rede, além de comunicação HTTPS. O caminho de inferência versionado é `/api/v1/predict`; mudanças incompatíveis de contrato requerem nova versão. Os erros propostos incluem 400 (JSON/estrutura malformados), 401/403 (autenticação/autorização), 422 (validação de campos ou categoria), 500 (falha interna) e 503 (serviço/modelo indisponível).

As inferências deverão ser rastreáveis por identificadores técnicos, timestamps e versões do modelo, evitando registrar dados pessoais desnecessários.

## 8. Limitações

A arquitetura representa uma proposta acadêmica. `GET /health` e `POST /api/v1/predict` são especificações, não endpoints funcionais; não há API implantada ou serviço aprovado para produção.

O modelo atual apresenta recall limitado e não foi validado em dados reais e temporais.

Os custos de erros de classificação e as políticas operacionais de concessão de crédito ainda precisam ser definidos.

O serviço não deverá aprovar ou negar crédito automaticamente apenas com base na classificação prevista.

## 9. Próximas atividades

- Implementar e validar os endpoints e contratos propostos em um ambiente autorizado, após definir requisitos operacionais.
- Definir a estratégia de empacotamento e versionamento do modelo.
- Propor logging e monitoramento.
- Estabelecer critérios de drift, retreinamento e governança do target.

## 10. Referências

- FIAP — Introdução ao CRISP-DM, seção Deployment.
- FIAP — Problema de Negócio e Variável-Alvo, seção MLOps.
- Desafio da Disciplina — PayFlow Credit Risk.
- `docs/modeling/avaliacao_modelo.md`.
