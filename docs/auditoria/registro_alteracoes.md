# Registro de alterações e validações

## Alterações

- Preservados o CSV bruto, o modelo v1, o threshold 0,20 e as métricas publicadas.
- Acrescentadas comparações de imputação, sensibilidade de threshold, Average Precision, Brier Skill Score, class weight, ablações, análise didática de leakage e métricas exploratórias por grupos.
- Incluídas sementes, versões, parâmetros e resultados completos em `reports/experiments/`.
- Simplificadas as dependências diretas e incluído `pytest` em `requirements-dev.txt`.
- Versionados o joblib e os metadados v1; o notebook reproduz o JSON, incluindo Brier Score, e preserva a baseline existente.
- Atualizados os notebooks, documentação, relatório Word e textos dos slides de modelagem, avaliação, monitoramento e conclusão.

## Validação registrada

- Scripts executados no ambiente limpo: `python -m src.experiments.development_validation` e `python -m src.experiments.complementary_analysis`; ambos terminaram com código 0 e reproduziram os CSVs e JSONs de `reports/experiments/`.
- Notebooks 01–04: 14, 12, 12 e 27 células executadas sem erro de célula no ambiente limpo. Notebook 04 reproduziu e conferiu os metadados. Serialização `n_jobs=1` evitou erro de encerramento do resource tracker; avisos de permissões do IPython/ZMQ do host persistem.
- Ambiente limpo: `pip install -r requirements-dev.txt` concluiu; última suíte completa: `20 passed in 17.63s`.
- Integridade: `git diff --check` concluiu sem erros de whitespace; Git apenas avisou a normalização CRLF de README e requirements. Todos os XMLs e relacionamentos do PPTX foram analisados e o pacote está íntegro; os textos dos slides foram conferidos.
- PowerPoint: quatro slides foram sincronizados; renderização visual não foi verificada.
- Relatório Word: conteúdo salvo com 10 tabelas; renderização visual não foi verificada.

## Limitações

A avaliação do teste já foi consultada; seus intervalos não são validação independente. A base não contém datas, custos operacionais, regras completas de target ou proveniência real das variáveis. A análise por grupos é exploratória e não demonstra fairness. Não foi implementada API, não houve A/B e não há validação de produção.
