# Contrato da API REST — PayFlow Credit Risk

## 1. Objetivo

Definir o contrato de comunicação entre o sistema de crédito da PayFlow e o serviço de inferência responsável pela estimativa de inadimplência em até 90 dias.

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

### 3.1 Campos de entrada

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

Os demais campos deverão ser informados, salvo se futuras regras de validação justificarem outro comportamento.

Valores categóricos deverão respeitar o vocabulário e as regras definidas na preparação dos dados. Categorias não vistas no treinamento não deverão ser aceitas silenciosamente sem uma política explícita.

### 3.2 Exemplo de requisição

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

1. Validar o esquema, os tipos e os valores recebidos.
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
| 400 | Requisição malformada ou campos inesperados |
| 401 | Cliente não autenticado |
| 422 | Dados incompatíveis com o esquema |
| 500 | Erro interno de processamento |
| 503 | Modelo temporariamente indisponível |

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
- Validação de dados de entrada.
- Restrição de acesso