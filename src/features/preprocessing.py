from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def criar_preprocessador(X):
    """
    Cria um pré-processador para variáveis numéricas
    e categóricas, sem ajustá-lo aos dados.

    Args:
        X: DataFrame com as variáveis preditoras.

    Returns:
        ColumnTransformer configurado.
    """

    numericas = X.select_dtypes(
        include=["number"]
    ).columns.tolist()

    categoricas = X.select_dtypes(
        include=["object", "category", "string"]
    ).columns.tolist()

    if len(numericas) + len(categoricas) != X.shape[1]:
        raise ValueError("Existem tipos de colunas não tratados.")

    pipeline_numerico = Pipeline([
        ("imputacao", SimpleImputer(strategy="median")),
        ("padronizacao", StandardScaler())
    ])

    pipeline_categorico = Pipeline([
        (
            "imputacao",
            SimpleImputer(strategy="most_frequent")
        ),
        (
            "encoding",
            OneHotEncoder(handle_unknown="ignore")
        )
    ])

    return ColumnTransformer([
        ("numericas", pipeline_numerico, numericas),
        ("categoricas", pipeline_categorico, categoricas)
    ])