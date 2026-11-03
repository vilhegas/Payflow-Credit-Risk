import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import pytest
import sklearn
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split


ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "modelo_payflow_v1.joblib"
METADATA_PATH = ROOT / "models" / "modelo_payflow_v1.json"
DATASET_PATH = ROOT / "data" / "raw" / "payflow_credit_risk.csv"


@pytest.fixture(scope="module")
def artifact_context():
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    dataset = pd.read_csv(DATASET_PATH)
    X = dataset[metadata["features"]]
    y = dataset[metadata["target"]]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    model = joblib.load(MODEL_PATH)
    return metadata, model, X_train, X_test, y_train, y_test


def test_model_joblib_loads_and_matches_metadata(artifact_context):
    metadata, model, _, _, _, _ = artifact_context
    assert metadata["arquivo_modelo"] == MODEL_PATH.name
    assert metadata["algoritmo"] == model.named_steps["modelo"].__class__.__name__
    assert metadata["features"] == list(model.feature_names_in_)
    assert len(metadata["features"]) == model.n_features_in_ == 17
    assert metadata["threshold"] == 0.20
    assert metadata["target"] == "default_90d"
    assert metadata["metricas_teste"]["Brier Score"] == pytest.approx(0.0977, abs=5e-5)
    assert metadata["versao_sklearn"] == sklearn.__version__


def test_artifact_excludes_leakage_and_interest_rate_features(artifact_context):
    metadata, _, _, _, _, _ = artifact_context
    excluded = {
        "id_cliente", "default_90d", "parcelas_pagas_ate_3m",
        "atraso_primeira_parcela_dias", "status_apos_90d", "juros_mensal_pct",
    }
    assert excluded.isdisjoint(metadata["features"])


def test_artifact_probabilities_are_reproducible(artifact_context):
    _, model, _, X_test, _, _ = artifact_context
    sample = X_test.head(20)
    first = model.predict_proba(sample)
    second = model.predict_proba(sample)
    np.testing.assert_allclose(first, second, rtol=0, atol=0)
    assert first.shape == (20, 2)
    assert np.isfinite(first).all()
    assert np.allclose(first.sum(axis=1), 1.0)


def test_artifact_reproduces_historical_test_baseline(artifact_context):
    metadata, model, _, X_test, _, y_test = artifact_context
    probabilities = model.predict_proba(X_test)[:, 1]
    predictions = (probabilities >= metadata["threshold"]).astype(int)
    assert accuracy_score(y_test, predictions) == pytest.approx(0.8270, abs=5e-5)
    assert precision_score(y_test, predictions) == pytest.approx(0.3376, abs=5e-5)
    assert recall_score(y_test, predictions) == pytest.approx(0.4344, abs=5e-5)
    assert f1_score(y_test, predictions) == pytest.approx(0.3799, abs=5e-5)
    assert confusion_matrix(y_test, predictions).tolist() == [[774, 104], [69, 53]]
    assert roc_auc_score(y_test, probabilities) == pytest.approx(0.7202, abs=5e-5)
    assert brier_score_loss(y_test, probabilities) == pytest.approx(0.0977, abs=5e-5)


def test_metadata_and_model_accept_portable_repository_relative_paths():
    assert MODEL_PATH.is_file()
    assert METADATA_PATH.is_file()
    assert DATASET_PATH.is_file()
    assert ROOT == Path(__file__).resolve().parents[1]


def test_historical_model_can_be_reproduced_in_a_temporary_directory(artifact_context, tmp_path):
    # Catches a broken or nondeterministic clean-clone procedure for the v1 artifact.
    from src.models.reproduce_v1 import reproduce_v1_artifacts

    metadata, original, _, X_test, _, _ = artifact_context
    artifact_path, metadata_path = reproduce_v1_artifacts(tmp_path)
    reproduced = joblib.load(artifact_path)
    reproduced_metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    np.testing.assert_allclose(
        reproduced.predict_proba(X_test), original.predict_proba(X_test), rtol=0, atol=1e-12
    )
    assert reproduced_metadata == metadata
