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
| A-02 | Status contraditório em documento de negócio | Média | `docs/business/problema_negocio.md` | O documento indicava “Planejamento inicial” | Atualizar status e registrar limitações | Corrigido e validado |
| A-03 | Threshold precisa de justificativa técnica e econômica | Alta | `docs/business/metricas.md`, `docs/modeling/avaliacao_modelo.md` | O threshold 0,20 foi escolhido principalmente pelo F1-score | Documentar trade-off entre precision/recall e custo de erro | Documentado como limitação |
| A-04 | Ausência de indicador de dado faltante no pipeline | Alta | `src/features/preprocessing.py` | O pré-processador usa `SimpleImputer` sem `add_indicator` | Adicionar parâmetro experimentável e manter baseline original | Corrigido e validado |
| A-05 | Sem testes automatizados para integridade e pipeline | Alta | `tests/` | Pasta vazia | Criar testes para baseline, esquema e pré-processamento | Corrigido e validado |
| A-06 | Contrato da API truncado | Alta | `docs/deployment/contrato_api.md` | Seção de segurança termina em “Restrição de acesso” | Completar regra de segurança e comportamento de categorias desconhecidas | Corrigido e validado |
| A-07 | Codificação do arquivo de dependências problemática | Média | `requirements.txt` | Arquivo em UTF-16 | Normalizar para UTF-8 legível e reproduzível | Corrigido e validado |
| A-08 | Falta de registro de mudanças e justificativas | Média | `docs/auditoria/registro_alteracoes.md` | Não havia rastreio de ajustes e evidências | Criar registro de alterações com métricas e validações | Corrigido e validado |

## 3. Dependências e ordem de execução

1. Verificação da baseline e do dataset.
2. Correção do pré-processador e testes de regressão.
3. Atualização de documentação de negócio e de métricas.
4. Completar o contrato de API e separar proposta de implementação real.
5. Validar os testes e consolidar o registro final.

## 4. Conclusão do diagnóstico

O repositório já estava coerente com a baseline histórica e a versão v1 do modelo. As inconsistências confirmadas são principalmente de documentação, de rastreabilidade, de reprodução e de contratos propostos. As correções implementadas preservam a baseline original e acrescentam validação metodológica sem inventar resultados novos.
