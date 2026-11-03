# Contrato da API REST — PayFlow Credit Risk

## 1. Objetivo

Definir uma proposta de contrato de comunicação entre o sistema de crédito da PayFlow e um futuro serviço de inferência responsável pela estimativa de inadimplência em até 90 dias. Este contrato é especificação acadêmica: nenhum endpoint está implementado ou implantado.

A API será proposta como um serviço de apoio à decisão, não como mecanismo autônomo de aprovação ou recusa de crédito.

## 2. Modelo utilizado

| Propriedade | Valor |
|---|---|
| Algoritmo | Regressão Logística |
| Threshold | 0,20 |
| Target | `default_90d` |
| Horizonte | 90 dias |
| Variáveis preditoras | 17 |
| Pré-processamento | Pipeline Scikit-learn |
| Formato de comunicação | JSON |

## 3. Endpoint de inferência

**Método:** `POST`

**Endpoint:** `/api/v1/predict`

**Content-Type:** `application/json`
A requisição deverá conter as 17 variáveis utilizadas no treinamento, com os mesmos nomes e tipos.

### 3.1 Verificação de saúde proposta

**Método:** `GET`
**Endpoint:** `/health`

Esta rota faz parte da proposta da versão 1. Deve indicar se o serviço está ativo e se o artefato do modelo está carregado, sem receber dados de clientes. Uma resposta de sucesso proposta é `200` com `{"status":"ok","model_loaded":true,"versao_modelo":"1.0.0"}`; indisponibilidade do modelo deve resultar em `503`. A rota é especificada, mas não implementada.

### 3.2 Campos de entrada

| Campo | Tipo | Descrição |
|---|---|---|
| `idade` | int | Idade do cliente |
| `renda_mensal` | float ou null | Renda mensal declarada |
| `tempo_emprego_anos` | float ou null | Tempo de emprego |
| `autonomo` | int (0/1) | Indicador de trabalho autônomo |
| `score_credito` | float | Score de crédito |
| `valor_solicitado` | float | Valor solicitado |
| `prazo_meses` | int | Prazo em meses |
| `qtde_cartoes` | int | Quantidade de cartões |
| `qtde_contratos_abertos` | int | Contratos em aberto |
| `utilizacao_credito` | float | Utilização de crédito |
| `inadimplencias_anteriores` | int | Histórico de inadimplência |
| `dias_atraso_max_12m` | int | Maior atraso nos últimos 12 meses |
| `reclamacoes_6m` | int | Reclamações nos últimos seis meses |
| `possui_avalista` | int (0/1) | Indicador de avalista |
| `canal_aquisicao` | string | Canal de aquisição |
| `regiao` | string | Região |
| `tipo_produto` | string | Produto de crédito |

Os campos de renda e tempo de emprego poderão conter valores nulos, tratados pelo pipeline de imputação treinado.

Os demais campos deverão ser informados. A camada da API será responsável por validar presença, tipo, valores permitidos e categorias antes de chamar o pipeline. As categorias observadas no CSV de treinamento são `canal_aquisicao` = `app`, `loja`, `parceiro`, `site`; `regiao` = `Centro-Oeste`, `Nordeste`, `Norte`, `Sudeste`, `Sul`; e `tipo_produto` = `bnpl`, `cartao`, `emprestimo_pessoal`. Essa lista descreve o vocabulário observado nos dados, não uma garantia de que represente todo o vocabulário operacional.

Categorias não vistas no treinamento serão rejeitadas pela validação da API com HTTP 422. Embora o `OneHotEncoder(handle_unknown="ignore")` do pipeline possa ignorá-las tecnicamente, o contrato proposto exige validação explícita para que uma categoria desconhecida não seja aceita silenciosamente.

### 3.3 Exemplo de requisição

Valores puramente ilustrativos; o exemplo não representa uma observação validada do dataset.

```json
{
  "idade": 35,
  "renda_mensal": 5500.0,
  "tempo_emprego_anos": 5.0,
  "autonomo": 0,
  "score_credito": 680,
  "valor_solicitado": 12000.0,
  "prazo_meses": 24,
  "qtde_cartoes": 2,
  "qtde_contratos_abertos": 1,
  "utilizacao_credito": 0.35,
  "inadimplencias_anteriores": 0,
  "dias_atraso_max_12m": 10,
  "reclamacoes_6m": 0,
  "possui_avalista": 0,
  "canal_aquisicao": "app",
  "regiao": "Sudeste",
  "tipo_produto": "emprestimo_pessoal"
}
```

O exemplo deverá ser adaptado aos valores categóricos efetivamente aceitos pelo pipeline antes de ser utilizado em testes.

## 4. Processamento interno

Após receber a requisição, o serviço deverá:

1. Validar o esquema, tipos, faixas e categorias recebidos; rejeitar campos ausentes, extras ou incompatíveis conforme os erros definidos abaixo.
2. Confirmar a disponibilidade das variáveis no momento da solicitação.
3. Organizar as entradas na estrutura esperada pelo pipeline.
4. Aplicar o pré-processamento já ajustado no treinamento.
5. Calcular a probabilidade com `predict_proba`.
6. Aplicar o threshold de 0,20.
7. Retornar a estimativa, a classificação e a versão do modelo.

O pré-processamento não poderá ser reajustado utilizando dados recebidos pela API.

## 5. Contrato de resposta

### 5.1 Exemplo de sucesso — HTTP 200

```json
{
  "probabilidade_default_90d": 0.27,
  "threshold": 0.20,
  "classificacao": 1,
  "modelo": "logistic_regression",
  "versao_modelo": "1.0.0",
  "horizonte_dias": 90
}
```

Esse resultado é hipotético. A probabilidade real somente será conhecida após executar a inferência com o modelo treinado.

### 5.2 Interpretação

- `classificacao = 0`: probabilidade estimada inferior a 0,20.
- `classificacao = 1`: probabilidade estimada maior ou igual a 0,20.

A classificação 1 indica uma sinalização de risco pelo modelo. Ela não representa uma determinação automática de inadimplência futura nem uma ordem para negar crédito.

## 6. Tratamento de erros

| Código HTTP | Situação |
|---|---|
| 200 | Inferência realizada |
| 400 | JSON malformado ou estrutura da requisição inválida |
| 401 | Cliente não autenticado |
| 403 | Cliente autenticado sem permissão |
| 422 | Campo ausente/extra, tipo ou valor inválido, ou categoria desconhecida |
| 500 | Erro interno de processamento |
| 503 | Modelo não carregado ou serviço temporariamente indisponível (inclui `/health`) |

### Exemplo de erro de validação

```json
{
  "erro": "validation_error",
  "mensagem": "Campo idade deve conter um numero inteiro.",
  "campo": "idade"
}
```

## 7. Segurança e privacidade

O serviço deverá contemplar:

- Autenticação e autorização dos sistemas consumidores.
- Comunicação protegida por HTTPS.
- Validação de dados de entrada, incluindo tipos, faixa de valores e presença de campos obrigatórios.
- Restrição de acesso por identidade do consumidor, regras de rede e permissões mínimas.
- Registro de eventos de inferência, falhas de validação e erros internos para governança e rastreabilidade.
- Tratamento explícito de categorias não previstas; no contrato proposto, categorias desconhecidas devem ser rejeitadas com erro de validação em vez de serem aceitas silenciosamente.
- Versionamento da interface de API, de modo que mudanças no schema ou no comportamento do modelo sejam rastreáveis.
- A rota de inferência é versionada no caminho (`/api/v1/predict`); alteração incompatível de schema ou semântica requer nova versão.

O uso do `OneHotEncoder(handle_unknown="ignore")` no treinamento não elimina a necessidade de adesão ao contrato. Em inferência, a API deve rejeitar categorias fora do vocabulário esperado e retornar uma resposta de erro de validação (HTTP 422), preservando a regra de negócio e reduzindo o risco de vazamento de informação por uso de entrada mal formada.

O documento descreve uma proposta de implantação: `/health` e `/api/v1/predict` não são endpoints implementados, e não existe implantação em produção. A implementação real exigiria controle de acesso, auditoria, políticas de segurança, governança de dados e monitoramento operacional específicos do ambiente em que o modelo passaria a atuar.
