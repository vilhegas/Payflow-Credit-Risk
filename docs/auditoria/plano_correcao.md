# Diagnóstico inicial e plano de correção

## 1. Evidências verificadas

- O dataset bruto possui 5.000 registros e 23 colunas.
- A taxa de default observada na variável alvo `default_90d` é 12,18%, confirmada no conjunto completo.
- A divisão estratificada 80/20 foi reproduzida e os resultados do baseline histórico foram confirmados: acurácia 82,70%, precision 33,76%, recall 43,44%, F1-score 37,99%, ROC-AUC 0,7202.
- O modelo escolhido e o threshold de 0,20 continuam consistentes com o artefato serializado em `models/modelo_payflow_v1.joblib` e nos metadados em `models/modelo_payflow_v1.json`.
- O repositório está em estado limpo do ponto de vista de alterações não rastreadas, com exceção de artefatos de apresentação e da documentação de auditoria em desenvolvimento.
- Há ausência de testes automatizados na pasta `tests/`.
- O arquivo `requirements.txt` está em codificação UTF-16, o que compromete portabilidade e leitura em ambientes que esperam UTF-8.
- O pipeline de pré-processamento ainda não expõe a opção `SimpleImputer(add_indicator=True)` para experimentos sobre ausência de renda e tempo de emprego.
- O contrato da API apresenta a seção de segurança truncada, sem conclusão e sem distinção explícita entre proposta de implantação e serviço real implementado.

## 2. Checklist de auditoria consolidado

| ID | Inconsistência | Prioridade | Arquivos afetados | Evidência | Correção | Status |
|---|---|---|---|---|---|---|
| A-01 | Definição operacional de default ainda precisa ser formalizada com cuidado | Alta | `docs/business/problema_negocio.md`, `docs/desafio/dicionario_dados_payflow.md` | O dataset fornece `default_90d`, mas não define a regra contratual que o produz | Documentar como limite metodológico e manter a variável como target observacional | Corrigido e validado |
| A-02 | Status contraditório em documentos de negócio e EDA | Média | `docs/business/problema_negocio.md`, `docs/data/conclusoes_eda.md` | Há status divergentes e pendências não consolidadas | Normalizar status de revisão e preservar limitações documentadas | Corrigido e validado |
| A-03 | Renda ausente e associação com default não foi tratada com evidência estatística adequada | Alta | `docs/data/conclusoes_eda.md`, `src/features/preprocessing.py` | Taxa de default foi 16,15% vs 12,02%; p ≈ 0,091 no teste exato de Fisher | Registrar como sugestão exploratória, não como associação confirmada; manter opção `use_missing_indicator` experimental | Corrigido e validado |
| A-04 | Ausência de indicador de dado faltante no pipeline | Alta | `src/features/preprocessing.py` | O pré-processador usava `SimpleImputer` sem `add_indicator` | Adicionar parâmetro experimentável e manter baseline original | Corrigido e validado |
| A-05 | Tempo de emprego ausente para autônomos não foi integrada corretamente ao processo de decisão | Média | `docs/data/conclusoes_eda.md`, `src/features/preprocessing.py` | 526 ausências concentradas em `autonomo = 1` | Registrar a concentração, comparar medianas e manter estratégia conservadora | Corrigido e validado |
| A-06 | Falta de validação de estratégias de imputação em dados de desenvolvimento | Alta | `src/features/preprocessing.py`, `tests/test_preprocessing_and_baseline.py` | A opção experimental não tinha evidência formal de comparação | Validar `median` versus `median + missing indicator` apenas em desenvolvimento | Corrigido e validado |
| A-07 | Threshold precisa de justificativa técnica e econômica | Alta | `docs/business/metricas.md`, `docs/modeling/avaliacao_modelo.md` | O threshold 0,20 foi escolhido principalmente pelo F1-score | Documentar trade-off entre precision/recall e custo de erro | Documentado como limitação |
| A-08 | Sem testes automatizados para integridade e pipeline | Alta | `tests/` | Pasta vazia | Criar testes para baseline, esquema e pré-processamento | Corrigido e validado |
| A-09 | Contrato da API truncado | Alta | `docs/deployment/contrato_api.md` | Seção de segurança terminava em “Restrição de acesso” | Completar regra de segurança e comportamento de categorias desconhecidas | Corrigido e validado |
| A-10 | API e deployment confluíram com funcionalidade real sem distinção clara | Alta | `docs/deployment/contrato_api.md`, `docs/deployment/arquitetura.md` | O documento misturava proposta com implementação | Separar proposta, requisitos e estado real de implementação | Corrigido e validado |
| A-11 | Codificação do arquivo de dependências problemática | Média | `requirements.txt` | Arquivo em UTF-16 | Normalizar para UTF-8 legível e reproduzível | Corrigido e validado |
| A-12 | Falta de registro de mudanças e justificativas | Média | `docs/auditoria/registro_alteracoes.md` | Não havia rastreio de ajustes e evidências | Criar registro de alterações com métricas e validações | Corrigido e validado |
| A-13 | Modelo e metadados não tinham Brier Score documentado de forma consistente | Média | `models/modelo_payflow_v1.json` | O artefato não registrava Brier Score e havia inconsistência entre documentação e JSON | Adicionar o valor verificado e manter a referência histórica | Corrigido e validado |
| A-14 | Ausência de validação de split e leakage em teste automatizado | Alta | `tests/test_preprocessing_and_baseline.py` | Não havia checagens do dataset e da separação | Adicionar testes de integridade, exclusão de leakage e baseline | Corrigido e validado |
| A-15 | EDA original misturava exploração descritiva com decisões supervisionadas do treino/teste | Média | `notebooks/02_eda.ipynb`, `docs/data/conclusoes_eda.md` | O conjunto completo foi usado antes da separação | Registrar o limite do uso histórico e preservar o holdout para novos experimentos | Documentado como limitação |

## 3. Dependências e ordem de execução

1. Verificação da baseline e do dataset.
2. Correção do pré-processador e testes de regressão.
3. Atualização de documentação de negócio e de métricas.
4. Completar o contrato de API e separar proposta de implementação real.
5. Validar os testes e consolidar o registro final.

## 4. Conclusão do diagnóstico

O repositório já estava coerente com a baseline histórica e a versão v1 do modelo. As inconsistências confirmadas são principalmente de documentação, de rastreabilidade, de reprodução e de contratos propostos. As correções implementadas preservam a baseline original e acrescentam validação metodológica sem inventar resultados novos.
