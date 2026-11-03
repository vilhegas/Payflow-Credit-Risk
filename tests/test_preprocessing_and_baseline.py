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


def test_pipeline_handles_missing_values_without_absolute_paths(feature_frame):
    preprocessor = criar_preprocessador(feature_frame)
    transformed = preprocessor.fit_transform(feature_frame)
    assert transformed.shape[0] == len(feature_frame)
    assert transformed.shape[1] > 0
