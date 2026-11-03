# Revisão final — resumo das decisões

A auditoria e suas evidências estão consolidadas em [`decisoes_limitacoes.md`](decisoes_limitacoes.md). Esse documento reúne a baseline, resultados de desenvolvimento, incerteza histórica, leakage, ablações, grupos, limitações temporais e proposta de implantação.

## Estado

- **Baseline v1:** preservada, com threshold 0,20, joblib e metadados versionados.
- **Experimentos:** executáveis e resultados completos versionados em `reports/experiments/`; somente os 4.000 registros de desenvolvimento são usados em seleção e ablações.
- **Testes e metadados:** verificam dados, pipeline, artefato, schema, versão do scikit-learn e métricas históricas. O notebook gera os metadados, inclui Brier e compara com o JSON preservado.
- **Documentação:** contratos de API e MLOps são propostas acadêmicas, sem implantação.
- **Entrega:** relatório Word atualizado; inspeção visual final indisponível neste host. O conteúdo do PowerPoint foi sincronizado e seu pacote XML validado, mas a renderização visual ainda não foi conferida.

## Referências

- [`decisoes_limitacoes.md`](decisoes_limitacoes.md) — síntese técnica e científica.
- [`registro_alteracoes.md`](registro_alteracoes.md) — alterações e validações resumidas.
- `docs/business/metricas.md` — baseline e métricas complementares.
- `reports/experiments/` — resultados numéricos e configurações completas.
