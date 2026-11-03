# Registro de alterações e evidências

## 1. Baseline histórico validado

Os números publicados no projeto foram reproduzidos no ambiente atual com a seguinte execução:

- 5.000 registros e 23 colunas no dataset bruto.
- taxa de default observada: 12,18%.
- divisão 80/20 estratificada, com 4.000 registros em treino e 1.000 no teste.
- Regressão Logística com threshold de 0,20.

Resultados confirmados:

| Métrica | Valor |
|---|---:|
| Acurácia | 82,70% |
| Precision | 33,76% |
| Recall | 43,44% |
| F1-score | 37,99% |
| ROC-AUC | 0,7202 |
| Matriz de confusão | TN=774, FP=104, FN=69, TP=53 |

Esses valores permaneceram como referência histórica e não foram substituídos por novos resultados experimentais.

## 2. Alterações implementadas

### 2.1. Pipeline de pré-processamento

- Adicionada a opção `use_missing_indicator` em `src/features/preprocessing.py`.
- A estratégia padrão continua igual à baseline original.
- Quando ativada, a imputação numérica passa a usar `SimpleImputer(strategy="median", add_indicator=True)` para permitir a análise de ausência como sinal preditivo.

### 2.2. Testes automatizados

- Criado o arquivo `tests/test_preprocessing_and_baseline.py`.
- Os testes validam:
  - shape do dataset e taxa de default;
  - presença dos indicadores de dados ausentes;
  - comportamento padrão do pipeline sem alteração da baseline.

### 2.3. Documentação e reprodutibilidade

- Criado o diagnóstico e checklist em `docs/auditoria/plano_correcao.md`.
- Atualizadas as descrições de business understanding e métricas para deixar explícita a limitação de informação sobre a regra contratual de default e a justificativa do threshold 0,20.
- Finalizada a seção de segurança do contrato de API em `docs/deployment/contrato_api.md`.
- Normalizada a codificação do arquivo de dependências para facilitar execução em ambientes compatíveis.

## 3. Validação executada

Comando executado:

```bash
cd "d:/FIAP/payflow-credit-risk" && .\.venv\Scripts\python.exe -m pytest tests/test_preprocessing_and_baseline.py -q
```

Resultado: 3 testes aprovados.

## 4. Limitações que permanecem

- Não há regra contratual de default documentada no conjunto de dados; a variável `default_90d` é tratada como indicador observacional.
- Os custos reais de falso positivo e falso negativo não foram fornecidos.
- Não foi possível transformar a proposta de implantação em implementação real sem ampliar o escopo do projeto e sem dados operacionais.
- O modelo e o threshold continuam sendo uma referência acadêmica e experimental e não uma política de concessão de crédito em produção.
