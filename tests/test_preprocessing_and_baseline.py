from pathlib import Path

import pandas as pd
import pytest

from src.features.preprocessing import criar_preprocessador


DATASET_PATH = Path(__file__).resolve().parents[1] / "data" / "raw" / "payflow_credit_risk.csv"


@pytest.fixture
def dataset():
    return pd.read_csv(DATASET_PATH)


def test_dataset_baseline_matches_expected_reference(dataset):
    assert dataset.shape == (5000, 23)
    assert dataset["default_90d"].mean() == pytest.approx(0.1218, abs=1e-4)
    assert dataset["renda_mensal"].isna().sum() == 192
    assert dataset["tempo_emprego_anos"].isna().sum() == 526


def test_preprocessor_supports_missing_indicator_option(dataset):
    features = dataset.drop(columns=["id_cliente", "default_90d", "parcelas_pagas_ate_3m", "atraso_primeira_parcela_dias", "status_apos_90d", "juros_mensal_pct"])

    preprocessor = criar_preprocessador(features, use_missing_indicator=True)
    preprocessor.fit(features)

    num_imputer = preprocessor.named_transformers_["numericas"].named_steps["imputacao"]
    assert getattr(num_imputer, "add_indicator", False) is True


def test_default_preprocessor_keeps_original_behavior(dataset):
    features = dataset.drop(columns=["id_cliente", "default_90d", "parcelas_pagas_ate_3m", "atraso_primeira_parcela_dias", "status_apos_90d", "juros_mensal_pct"])

    preprocessor = criar_preprocessador(features)
    preprocessor.fit(features)

    num_imputer = preprocessor.named_transformers_["numericas"].named_steps["imputacao"]
    assert getattr(num_imputer, "add_indicator", False) is False
