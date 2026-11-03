# Decisões, evidências e limitações

## Escopo e estado

Este projeto é uma entrega acadêmica baseada em dados sintéticos. O modelo v1 e o threshold histórico 0,20 foram preservados. Experimentos de seleção e ablação usam os 4.000 registros de desenvolvimento. O teste histórico de 1.000 registros já foi consultado; seus intervalos de confiança apenas quantificam a incerteza da avaliação publicada e não constituem validação independente.

## Baseline histórica

| Medida no teste histórico | Resultado |
|---|---:|
| Accuracy | 0,8270 |
| Precision | 0,3376 |
| Recall | 0,4344 |
| F1 | 0,3799 |
| ROC-AUC | 0,7202 |
| Brier Score | 0,0977 |
| Matriz TN, FP, FN, TP | 774, 104, 69, 53 |

O artefato `models/modelo_payflow_v1.joblib`, seus metadados, dataset bruto e threshold não foram substituídos. A geração de metadados é feita por código, inclui Brier Score e compara os valores reproduzidos com o JSON histórico.

## Comparação de modelos em desenvolvimento

Todos os modelos abaixo usam os mesmos folds estratificados (5, `random_state=42`), as mesmas features-base e threshold 0,20 para métricas de classe. `ROC-AUC OOF` é calculada uma vez sobre as predições OOF concatenadas; não é a média das cinco ROC-AUCs por fold. Para a Regressão Logística, a média por fold é 0,7762 e a AUC OOF concatenada é 0,7743; para Random Forest, são 0,7727 e 0,7719. O resultado de teste histórico (0,7202) é separado e não participou da seleção. Average Precision é calculada com `average_precision_score`; ela resume a curva precision-recall por soma ponderada dos ganhos de recall e não é a área trapezoidal da curva. A prevalência de default, 0,12175, é uma referência não informativa aproximada para Average Precision.

| Experimento | ROC-AUC OOF | AP OOF | Precision | Recall | F1 | Brier | Brier Skill |
|---|---:|---:|---:|---:|---:|---:|---:|
| Regressão Logística | 0,7743 | 0,3799 | 0,3670 | 0,4702 | 0,4122 | 0,0911 | 0,1478 |
| Random Forest | 0,7719 | 0,3907 | 0,3699 | 0,4990 | 0,4248 | 0,0916 | 0,1430 |
| Regressão Logística, class weight balanceado | 0,7726 | 0,3783 | 0,1421 | 0,9569 | 0,2474 | 0,1843 | -0,7238 |

A Random Forest teve F1 e Average Precision maiores nesta validação, enquanto a Regressão Logística teve ROC-AUC e Brier ligeiramente melhores. A Regressão Logística permanece como referência por simplicidade e interpretabilidade, aceitando a diferença observada de F1. Nos cinco folds pareados, a diferença ROC-AUC LR−RF variou de -0,0242 a 0,0248, com média +0,0035. Essa variação não é teste de equivalência nem sustenta superioridade estatística. Os valores por fold estão em `reports/experiments/diferencas_pareadas_folds.csv`. A escolha e o threshold foram examinados no mesmo conjunto de desenvolvimento, portanto as métricas de seleção podem ser otimistas.

O Brier Skill Score é `1 − Brier(modelo) / Brier(referência)`. Na validação OOF, cada linha de validação é comparada à prevalência calculada somente no treino do fold correspondente. Valor positivo supera o preditor constante de referência em erro quadrático; valor negativo indica erro maior. O resultado de `class_weight="balanced"` mostra forte ganho de recall no corte 0,20, acompanhado de baixa precision e pior calibração; não substituiu a baseline.

## Incerteza do teste já consultado

Bootstrap pareado por observação (5.000 reamostragens, semente 42, percentis 2,5 e 97,5%). Reamostragens sem classes suficientes são descartadas explicitamente. Neste conjunto, nenhuma reamostragem foi descartada.

| Métrica histórica | Estimativa | IC 95% |
|---|---:|---:|
| ROC-AUC | 0,7202 | 0,6665–0,7726 |
| Precision, threshold 0,20 | 0,3376 | 0,2642–0,4140 |
| Recall, threshold 0,20 | 0,4344 | 0,3475–0,5254 |

Esses intervalos descrevem apenas a incerteza amostral do resultado histórico. Não foram usados para escolher configuração e não tornam a avaliação independente. Resultados completos e contagens de reamostragem estão em `reports/experiments/intervalos_teste_historico.json`.

## Features, leakage e grupos

A inspeção direta do CSV encontrou que a condição `parcelas_pagas_ate_3m <= 1` reproduz o target em 5.000/5.000 linhas: os 4.391 casos com target 0 ficam acima de 1 parcela paga e os 609 casos com target 1 ficam em 0 ou 1 parcela paga. A condição `atraso_primeira_parcela_dias > 15` coincide com o target em 4.999/5.000 linhas; a única exceção tem atraso de 15 dias e target 1. Essas relações não provam que sejam a fórmula de geração ou a regra contratual do target. O código disponível não documenta essa proveniência, que permanece pendente.

As duas variáveis posteriores foram testadas apenas como demonstração didática e nunca como candidatas para uso. Com `parcelas_pagas_ate_3m`, a ROC-AUC OOF observada foi 1,0000; com `atraso_primeira_parcela_dias`, 0,9991; juntas, 1,0000. Essa separação quase perfeita ilustra que informação produzida depois da concessão permite reconhecer o desfecho e não estaria disponível no momento legítimo da decisão. O rótulo não deve ser descrito como “90 dias consecutivos em atraso”: o horizonte de observação não especifica o evento contratual que gera default.

No desenvolvimento, a correlação de Pearson entre `juros_mensal_pct` e `score_credito` foi -0,8007. Isso pode ser compatível com precificação relacionada ao risco, mas não demonstra a ordem operacional nem causalidade. Incluir a taxa alterou ROC-AUC OOF de 0,7743 para 0,7753 e Brier de 0,0911 para 0,0910; a feature segue excluída até sua disponibilidade no instante da decisão ser validada.

As ablações com as mesmas dobras deram ROC-AUC/AP OOF de 0,7760/0,3824 sem região e 0,7773/0,3828 sem região, idade e canal. A ligeira variação não é critério automático de remoção. As tabelas exploratórias por região, canal e quartis de idade usam as previsões OOF da Regressão Logística no corte 0,20 e estão em `reports/experiments/analise_grupos_desenvolvimento.csv`. Há pelo menos 265 observações em cada grupo apresentado, mas diferenças de prevalência, sinalização, recall e precision não estabelecem viés ou justiça. A análise é limitada, sem intervalos por grupo nem avaliação de proxies, impacto ou atributos protegidos suficientes.

## Horizonte, fontes e validação futura

A janela de 90 dias pode permitir que um evento de inadimplência amadureça, acompanhe um ciclo inicial de cobrança e gere rótulo em prazo ainda útil para acompanhamento. Janelas menores podem acelerar o retorno, mas deixar eventos tardios sem observação; janelas maiores ampliam a maturação e atrasam a avaliação. Esta é uma justificativa conceitual, não a motivação original comprovada do CSV nem uma regra contratual de default. O critério que gera `default_90d` permanece por confirmar.

As possíveis fontes operacionais são hipóteses para validação: cadastro e contato em CRM/atendimento; solicitação e condições em originação; score em bureaus; interação/canal em aplicativos; renda, obrigações e pagamentos em sistemas financeiros. Disponibilidade, atualização, defasagem e elegibilidade temporal de cada coluna devem ser documentadas com os sistemas reais. Essas fontes não são origens confirmadas do dataset sintético.

Uma avaliação futura deveria identificar safras e datas reais de concessão, separar treino e teste cronologicamente, treinar em safras anteriores e avaliar em safras posteriores (out-of-time), aguardando maturação completa do target. O split aleatório 80/20 atual pode misturar períodos e não representa essa mudança temporal. Não foram criadas datas artificiais.

## Implantação e monitoramento propostos

Antes de qualquer decisão automatizada: validação offline; execução em shadow mode; piloto reduzido com revisão humana; comparação com a política vigente; monitoramento de efeitos e critérios de interrupção acordados. Um desenho A/B exigiria hipótese, MDE, tamanho de amostra, duração, salvaguardas e autorização de risco/compliance; esses parâmetros dependem de dados operacionais ainda indisponíveis. Nenhum A/B ou deployment foi realizado.

Monitorar qualidade e drift dos dados, probabilidades, taxa de sinalização, ROC-AUC, Average Precision, recall, Brier e indicadores operacionais. Referências PSI 0,10 e 0,25, se usadas, são heurísticas iniciais, sujeitas à calibração, tamanho da amostra e contexto; não são limites universais. Métricas com rótulo devem aguardar o horizonte completo de 90 dias.

## Próximas hipóteses para v2 (não implementadas)

- Avaliar `valor_solicitado / renda_mensal` com tratamento explícito de renda ausente/zero e validação temporal da disponibilidade dos campos.
- Comparar lift/gains por faixas de score, com intervalos de incerteza e avaliação em dados não usados na seleção.
- Estudar otimização do threshold somente após obter custos e objetivos operacionais aprovados; não presumir valores financeiros.
- Tratar `valor_solicitado` como possível proxy de exposição, sujeito a definição de exposição efetiva e validação com dados operacionais; não equivale a EAD comprovada.

Esses itens são propostas de investigação e não fazem parte do modelo, dos resultados ou dos artefatos v1 atuais.

## Artefatos reprodutíveis

- `python -m src.experiments.development_validation`: imputação e sensibilidade de threshold.
- `python -m src.experiments.complementary_analysis`: métricas adicionais, ablações, leakage, fairness exploratória e bootstrap histórico.
- `python -m pytest -q -p no:cacheprovider`: suíte de testes.
- `reports/experiments/`: CSVs e JSONs completos, parâmetros, sementes e versões.

O contrato de API, shadow mode, piloto e monitoramento são propostas acadêmicas. Não existe API funcional ou validação operacional. O relatório Word e os notebooks são conteúdo acadêmico; o PowerPoint deve refletir esses mesmos limites.
