# Entendimento do Problema de Negócio — Business Understanding

**Projeto:** Credit Risk — Score de Inadimplência  
**Fase:** 1 — Business Understanding  
**Status:** Planejamento inicial

---

## 1. Contexto do negócio

A PayFlow é uma fintech fictícia que oferece soluções de crédito digital por meio de três modalidades:

- Empréstimo pessoal;
- Cartão de crédito;
- BNPL (*Buy Now, Pay Later* — compre agora, pague depois).

Nos últimos meses, a empresa identificou um aumento da inadimplência durante os primeiros 90 dias após a concessão de crédito.

Esse cenário compromete a sustentabilidade da carteira e dificulta a expansão das operações.

A diretoria busca melhorar a consistência e a escalabilidade das decisões de crédito, reduzindo a dependência exclusiva de regras manuais.

## 2. Dor do negócio

O desafio identifica três problemas principais:

| Problema | Consequência |
|---|---|
| Perdas financeiras | A inadimplência compromete os resultados financeiros da carteira. |
| Sobrecarga operacional | O aumento dos clientes inadimplentes amplia a demanda da equipe de cobrança. |
| Crescimento limitado | O receio de aumentar o risco da carteira dificulta a expansão da concessão de crédito. |

**Problema central:** a PayFlow precisa identificar antecipadamente clientes com maior probabilidade de inadimplência para melhorar suas decisões de concessão de crédito.

## 3. Stakeholders

O enunciado identifica a diretoria e a equipe de cobrança. A tabela também propõe outros participantes relevantes para uma operação de crédito.

| Stakeholder | Responsabilidade ou interesse |
|---|---|
| Diretoria | Acompanhar resultados financeiros e definir objetivos estratégicos. |
| Equipe de Crédito | Utilizar informações de risco para apoiar a análise de solicitações. |
| Equipe de Riscos | Definir políticas, limites e critérios de avaliação do risco. |
| Equipe de Cobrança | Planejar recursos e acompanhar a inadimplência. |
| Equipe de Dados | Desenvolver, avaliar e documentar a solução preditiva. |
| Compliance e Governança | Avaliar controles, rastreabilidade e uso adequado das informações. |

## 4. Objetivo de negócio

Apoiar decisões de concessão de crédito mais consistentes, escaláveis e orientadas a dados, com o propósito de reduzir a exposição à inadimplência nos primeiros 90 dias.

Resultados de negócio desejados:

- Reduzir perdas financeiras associadas à inadimplência.
- Melhorar a identificação antecipada de operações de maior risco.
- Apoiar uma concessão de crédito mais sustentável.
- Produzir informações que auxiliem o planejamento operacional.

Esses resultados são objetivos esperados, não resultados já alcançados.

## 5. Objetivo analítico

Desenvolver e avaliar uma solução de classificação binária capaz de estimar a probabilidade de um cliente entrar em default em até 90 dias após a concessão de crédito.

A previsão deverá utilizar somente informações disponíveis no momento da decisão.

### 5.1 Variável-alvo

| Propriedade | Definição |
|---|---|
| Target | `default_90d` |
| Tipo | Binária |
| Valor 0 | Cliente não classificado em default na janela observada |
| Valor 1 | Cliente classificado em default em até 90 dias |
| Unidade do dataset | Cliente, identificado por `id_cliente` |
| Horizonte | Primeiros 90 dias após a concessão |

### 5.2 Definição operacional de default

O dataset apresenta o resultado de default, mas não informa a regra contratual exata utilizada para classificá-lo.

Portanto, adotaremos inicialmente a classificação fornecida pela variável `default_90d`.

**Pendência de definição:** documentar o critério operacional que gera esse indicador, incluindo o atraso ou evento contratual necessário para caracterizar default.

Não devemos presumir que default signifique automaticamente 90 dias de atraso: o horizonte de observação e o critério de inadimplência são conceitos diferentes.

### 5.3 Momento da previsão

O momento de referência será a avaliação da solicitação de crédito, antes da concessão.

Isso significa que informações produzidas após a concessão não poderão ser utilizadas como variáveis preditoras.

## 6. Decisão de negócio que será melhorada

A solução deverá apoiar a avaliação de risco de novas solicitações de crédito.

O modelo produzirá uma probabilidade estimada de inadimplência, que poderá subsidiar políticas como:

- Encaminhamento de solicitações para análise adicional;
- Priorização de avaliações de risco;
- Aplicação de critérios de concessão definidos pela empresa.

A política definitiva não será determinada exclusivamente pelo algoritmo. Será necessário considerar as métricas, os custos dos erros e a governança das decisões.

## 7. Restrições e riscos identificados

### 7.1 Vazamento de informação (Data Leakage)

O dicionário de dados identifica três variáveis que contêm informações posteriores à concessão:

- `parcelas_pagas_ate_3m`
- `atraso_primeira_parcela_dias`
- `status_apos_90d`

Essas variáveis deverão ser excluídas das entradas do modelo de concessão, pois suas informações não estarão disponíveis no momento da previsão.

### 7.2 Dados sintéticos

A base fornecida é sintética e representa uma operação simulada.

Assim, o desempenho obtido nos experimentos não comprovará a efetividade da solução em uma instituição financeira real.

### 7.3 Disponibilidade temporal

O dicionário fornecido não identifica uma coluna de data de solicitação ou concessão.

Essa limitação precisará ser considerada na escolha da estratégia de validação.

### 7.4 Disponibilidade das variáveis

Cada variável deverá ser examinada para verificar se estaria disponível no momento da decisão. A elegibilidade não depende apenas de a coluna estar presente no CSV.

## 8. Resultados esperados desta fase

Ao concluir o Business Understanding, o projeto deverá apresentar:

- Problema de negócio documentado;
- Stakeholders e responsabilidades identificados;
- Objetivo de negócio definido;
- Objetivo analítico definido;
- Variável-alvo identificada;
- Horizonte de previsão estabelecido;
- Momento de decisão especificado;
- Restrições e premissas registradas.

As metas quantitativas e os critérios mensuráveis de sucesso serão definidos no documento `metricas.md`.

---

## 9. Referências utilizadas

**Materiais:**

- Introdução ao CRISP-DM — Capítulo 01;
- Definição do Problema de Negócio e Variável-Alvo — Capítulo 02;
- Metas de Negócio vs. Metas Analíticas — Capítulo 03;
- Como Transformar uma Dor de Negócio em Solução de Dados — Capítulo 04.

**Arquivos do desafio:**

- `Desafio_Disciplina_PayFlow_Credit_Risk.docx`;
- `dicionario_dados_payflow.md`.