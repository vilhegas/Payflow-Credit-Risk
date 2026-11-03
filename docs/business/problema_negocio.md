# Entendimento do Problema de Negócio — Business Understanding

**Projeto:** Credit Risk — Score de Inadimplência  
**Fase:** 1 — Business Understanding  
**Status:** Fase documentada para o escopo acadêmico; definições operacionais e validação de negócio permanecem pendentes de evidência da PayFlow

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

### Disponibilidade da taxa de juros

`valor_solicitado` e `prazo_meses` podem representar condições fornecidas antecipadamente na solicitação. A taxa `juros_mensal_pct`, por sua vez, pode ser uma condição contratual estabelecida depois da avaliação e pode ser precificada a partir do risco. Usá-la antes da confirmação da ordem operacional poderia gerar circularidade entre score e taxa ou usar informação posterior ao momento da previsão. Como o material do desafio não documenta essa sequência, não a tratamos como fato: a taxa fica excluída até que a disponibilidade no instante de decisão seja demonstrada.

### Por que observar 90 dias

Uma janela de 90 dias pode equilibrar a maturação de eventos de inadimplência, o ciclo inicial de cobrança e a utilidade de obter um rótulo em prazo que ainda permita acompanhar a carteira. Uma janela curta acelera a avaliação, mas pode não observar eventos tardios; uma janela longa inclui mais tempo de maturação e posterga a confirmação do resultado. Essa é uma justificativa conceitual para o horizonte do desafio, não uma explicação comprovada de como o dataset sintético foi construído. O horizonte de observação também não define, por si só, a regra contratual de default.

### Concepção das fontes de dados

O CSV não comprova a origem de nenhuma variável. A tabela traz hipóteses de arquitetura conceitual, não linhagem confirmada. Disponibilidade e defasagem precisam ser verificadas com os sistemas reais antes de usar qualquer campo.

| Grupo e exemplos | Fonte operacional hipotética | Disponibilidade estimada | Defasagem possível | Risco temporal e validação necessária |
|---|---|---|---|---|
| Perfil e cadastro: `idade`, `regiao`, `renda_mensal`, `autonomo`, `tempo_emprego_anos` | CRM, cadastro e originação | Cadastro ou solicitação | Atualização cadastral pode ocorrer depois ou estar desatualizada | Confirmar snapshot usado na decisão, data de atualização e fonte autorizada |
| Histórico de crédito: `score_credito`, `inadimplencias_anteriores`, `dias_atraso_max_12m`, `utilizacao_credito`, `qtde_contratos_abertos` | Bureaus e sistemas financeiros | Consulta de bureau ou visão financeira anterior à decisão | Atualização do bureau, fechamento de ciclo e latência de consulta | Verificar timestamp da consulta, janela histórica e se o valor existia no instante de concessão |
| Solicitação: `valor_solicitado`, `prazo_meses`, `tipo_produto` | Sistema de originação | Preenchimento da proposta | Condições podem mudar durante oferta ou negociação | Congelar a versão da proposta usada na avaliação |
| Canal, contato e relacionamento: `canal_aquisicao`, `reclamacoes_6m`, `qtde_cartoes`, `possui_avalista` | Aplicativos, CRM, atendimento e originação | Canal na entrada; demais dados conforme consulta ou cadastro | Sincronização de eventos, atendimento em aberto ou mudança após a proposta | Confirmar definição, janela temporal e instante de captura de cada campo |
| Preço: `juros_mensal_pct` | Motor de precificação e sistema financeiro | Possivelmente depois da avaliação de risco | Oferta ou contrato pode ser registrado após o score | Risco de circularidade e informação futura; validar a ordem real antes de remover a exclusão preventiva |
| Desfechos posteriores: parcelas pagas, atraso inicial e status aos 90 dias | Cobrança e sistema financeiro | Após a concessão | Depende da maturação dos pagamentos e consolidação | São informação futura para a decisão inicial e permanecem excluídas; validar definição do target separadamente |

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
