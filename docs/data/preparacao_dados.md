# Preparação dos Dados — Data Preparation

**Projeto:** PayFlow Credit Risk  
**Metodologia:** CRISP-DM  
**Fase:** Data Preparation

## 1. Objetivo

Preparar o conjunto de dados para a modelagem preditiva de inadimplência em 90 dias, garantindo consistência, reprodutibilidade e prevenção de vazamento de informações.

## 2. Seleção de variáveis

- Dataset original: 23 colunas e 5.000 registros.
- Variável-alvo: `default_90d`.
- Variáveis preditoras selecionadas: 17.
- Variáveis geradas após o pré-processamento: 26.

Foram excluídas das features:

- `id_cliente`: identificador.
- `default_90d`: variável-alvo.
- `parcelas_pagas_ate_3m`: informação futura.
- `atraso_primeira_parcela_dias`: informação futura.
- `status_apos_90d`: informação futura.
- `juros_mensal_pct`: excluída preventivamente enquanto não houver evidência de sua disponibilidade no instante previsto para a decisão.

Na inspeção do CSV, `parcelas_pagas_ate_3m <= 1` reproduz o target em 5.000/5.000 registros; `atraso_primeira_parcela_dias > 15`, em 4.999/5.000 (uma exceção: target 1 com atraso de 15 dias). A coincidência reforça a exclusão preventiva dessas colunas futuras, mas não revela a regra contratual nem prova como o target foi gerado.

`valor_solicitado` e `prazo_meses` representam condições que podem ser informadas como parte da solicitação antes da análise do risco. Já `juros_mensal_pct` pode ser definida posteriormente como condição contratual e pode refletir precificação baseada no próprio risco. Se a taxa for determinada após o score, seu uso introduziria informação indisponível no momento da previsão ou circularidade entre score e preço. A ordem efetiva do fluxo da PayFlow não está documentada; portanto, esta é uma justificativa metodológica, não uma afirmação sobre a operação real. A exclusão será mantida até que a disponibilidade temporal seja comprovada.

## 3. Divisão de dados

Aplicou-se uma divisão estratificada de 80% para treinamento e 20% para teste, utilizando `random_state=42`.

| Conjunto | Registros | Default |
|---|---:|---:|
| Treinamento | 4.000 | 12,18% |
| Teste | 1.000 | 12,20% |

O dataset não apresenta data de concessão, impossibilitando uma validação temporal baseada nas informações fornecidas.

## 4. Transformações aplicadas

| Tipo | Tratamento |
|---|---|
| Numéricas ausentes | Imputação pela mediana |
| Categóricas ausentes | Imputação pela categoria mais frequente |
| Variáveis categóricas | One-Hot Encoding |
| Variáveis numéricas | Padronização com StandardScaler |

As transformações foram ajustadas exclusivamente no conjunto de treinamento.

## 5. Outliers

Os possíveis outliers identificados na EDA foram mantidos.

O método IQR identifica observações extremas, mas não determina automaticamente que sejam inválidas.

O impacto desses valores deverá ser considerado durante a avaliação dos modelos.

## 6. Validações realizadas

As saídas salvas no notebook indicam:

- Integridade das dimensões aprovada;
- Nenhum NaN após as transformações;
- Mesma quantidade de features nos conjuntos;
- Ausência das colunas proibidas;
- Função reutilizável de pré-processamento importada com sucesso.

## 7. Reprodutibilidade

O pré-processamento foi organizado em:

`src/features/preprocessing.py`

A função `criar_preprocessador()` retorna um `ColumnTransformer` configurado, permitindo integrá-lo ao pipeline de treinamento dos modelos.

Durante a validação cruzada, as transformações deverão ser ajustadas separadamente dentro de cada divisão de treinamento.

## 8. Limitações

A base é sintética. A disponibilidade temporal de todas as variáveis candidatas ainda precisa ser confirmada em um cenário operacional real.

A definição exata de default também depende de documentação adicional da regra de negócio.


## 9. Referências

- FIAP — Introdução ao CRISP-DM, páginas 11–12.
- FIAP — Boas Práticas de Programação e Documentação (Cookiecutter).
- Dicionário de dados PayFlow.
- `03_preparacao.ipynb`.
- `preprocessing.py`.
