from pathlib import Path

import pandas as pd
import pytest

from src.features.preprocessing import criar_preprocessador


DATASET_PATH = Path(__file__).resolve().parents[1] / "data" / "raw" / "payflow_credit_risk.csv"
LEAKAGE_COLUMNS = [
    "id_cliente",
    "default_90d",
    "parcelas_pagas_ate_3m",
    "atraso_primeira_parcela_dias",
    "status_apos_90d",
    "juros_mensal_pct",
]


@pytest.fixture
def dataset():
    return pd.read_csv(DATASET_PATH)


@pytest.fixture
def feature_frame(dataset):
    return dataset.drop(columns=LEAKAGE_COLUMNS)


def test_dataset_baseline_matches_expected_reference(dataset):
    assert dataset.shape == (5000, 23)
    assert dataset.columns.is_unique
    assert dataset["id_cliente"].is_unique
    assert dataset["default_90d"].isin([0, 1]).all()
    assert dataset["default_90d"].mean() == pytest.approx(0.1218, abs=1e-4)
    assert dataset["renda_mensal"].isna().sum() == 192
    assert dataset["tempo_emprego_anos"].isna().sum() == 526


def test_train_test_split_is_stratified_and_preserves_target_rate(dataset):
    from sklearn.model_selection import train_test_split

    X = dataset.drop(columns=["id_cliente", "default_90d", "parcelas_pagas_ate_3m", "atraso_primeira_parcela_dias", "status_apos_90d", "juros_mensal_pct"])
    y = dataset["default_90d"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

    assert len(X_train) == 4000
    assert len(X_test) == 1000
    assert y_train.mean() == pytest.approx(0.1218, abs=1e-3)
    assert y_test.mean() == pytest.approx(0.1218, abs=1e-3)


def test_train_test_split_reproduces_historical_row_membership(dataset):
    from sklearn.model_selection import train_test_split

    first_train, first_test = train_test_split(
        dataset.index,
        test_size=0.20,
        stratify=dataset["default_90d"],
        random_state=42,
    )
    second_train, second_test = train_test_split(
        dataset.index,
        test_size=0.20,
        stratify=dataset["default_90d"],
        random_state=42,
    )
    assert len(first_train) == 4000 and len(first_test) == 1000
    assert first_train.equals(second_train)
    assert first_test.equals(second_test)
    assert set(first_train).isdisjoint(first_test)


def test_leakage_columns_are_excluded_from_training_features(feature_frame):
    expected = {"id_cliente", "default_90d", "parcelas_pagas_ate_3m", "atraso_primeira_parcela_dias", "status_apos_90d", "juros_mensal_pct"}
    assert set(expected).isdisjoint(feature_frame.columns)


def test_preprocessor_supports_missing_indicator_option(feature_frame):
    preprocessor = criar_preprocessador(feature_frame, use_missing_indicator=True)
    preprocessor.fit(feature_frame)

    num_imputer = preprocessor.named_transformers_["numericas"].named_steps["imputacao"]
    assert getattr(num_imputer, "add_indicator", False) is True


def test_default_preprocessor_keeps_original_behavior(feature_frame):
    preprocessor = criar_preprocessador(feature_frame)
    preprocessor.fit(feature_frame)

    num_imputer = preprocessor.named_transformers_["numericas"].named_steps["imputacao"]
    assert getattr(num_imputer, "add_indicator", False) is False


def test_preprocessor_handles_missing_values(feature_frame):
    preprocessor = criar_preprocessador(feature_frame)
    transformed = preprocessor.fit_transform(feature_frame)
    assert transformed.shape[0] == len(feature_frame)
    assert transformed.shape[1] > 0


def test_preprocessor_preserves_feature_count_and_input_order(feature_frame):
    preprocessor = criar_preprocessador(feature_frame)
    transformed = preprocessor.fit_transform(feature_frame)
    assert list(preprocessor.feature_names_in_) == list(feature_frame.columns)
    assert transformed.shape[0] == feature_frame.shape[0]
    numeric_count = len(feature_frame.select_dtypes(include=["number"]).columns)
    categorical_count = sum(
        len(categories)
        for categories in preprocessor.named_transformers_["categoricas"]
        .named_steps["encoding"].categories_
    )
    assert transformed.shape[1] == numeric_count + categorical_count


def test_unknown_categories_are_ignored_by_fitted_encoder(feature_frame):
    preprocessor = criar_preprocessador(feature_frame)
    preprocessor.fit(feature_frame)
    changed = feature_frame.head(1).copy()
    changed.loc[changed.index[0], "tipo_produto"] = "categoria_nao_observada"
    transformed = preprocessor.transform(changed)
    assert transformed.shape[0] == 1
    assert transformed.shape[1] == preprocessor.transform(feature_frame.head(1)).shape[1]


def test_preprocessing_is_fitted_inside_each_validation_fold():
    import numpy as np
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import KFold, cross_validate
    from sklearn.pipeline import Pipeline

    categories = ["heldout_only"] * 10 + ["known"] * 30
    X = pd.DataFrame({
        "idade": np.arange(40, dtype=float),
        "canal_aquisicao": categories,
    })
    y = pd.Series([0, 1] * 20)
    cv = KFold(n_splits=4, shuffle=False)
    pipeline = Pipeline([
        ("preprocessing", criar_preprocessador(X)),
        ("model", LogisticRegression()),
    ])
    result = cross_validate(pipeline, X, y, cv=cv, return_estimator=True)
    for (train_indices, _), fitted in zip(cv.split(X), result["estimator"]):
        preprocessor = fitted.named_steps["preprocessing"]
        actual_median = preprocessor.named_transformers_["numericas"].named_steps["imputacao"].statistics_[0]
        expected_median = float(X.iloc[train_indices, 0].median())
        assert actual_median == pytest.approx(expected_median)
    first_fold_categories = (
        result["estimator"][0]
        .named_steps["preprocessing"]
        .named_transformers_["categoricas"]
        .named_steps["encoding"].categories_[0]
    )
    assert first_fold_categories.tolist() == ["known"]
    assert result["estimator"][0].named_steps["preprocessing"].named_transformers_["numericas"].named_steps["imputacao"].statistics_[0] != pytest.approx(float(X.iloc[:, 0].median()))
