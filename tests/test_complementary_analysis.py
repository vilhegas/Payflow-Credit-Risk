import numpy as np
import pytest

from src.experiments.complementary_analysis import brier_skill_score, bootstrap_metric_ci
from src.models.metadata import build_model_metadata


def test_brier_skill_score_uses_training_prevalence_as_reference():
    # Catches substituting evaluation prevalence for the separately supplied training prevalence.
    observed = brier_skill_score([0, 1, 0, 1], [0.1, 0.8, 0.2, 0.7], reference_prevalence=0.25)
    assert observed == pytest.approx(1 - 0.045 / 0.3125)


def test_bootstrap_metric_ci_is_reproducible_and_reports_skipped_replicates():
    # Catches unseeded intervals and silently retaining bootstrap samples without both classes.
    y = np.array([0, 0, 0, 1, 1, 1])
    scores = np.array([0.1, 0.2, 0.4, 0.6, 0.8, 0.9])
    first = bootstrap_metric_ci(y, scores, metric="roc_auc", seed=7, n_resamples=200)
    second = bootstrap_metric_ci(y, scores, metric="roc_auc", seed=7, n_resamples=200)
    assert first == second
    assert first["valid_resamples"] > 0
    assert first["skipped_resamples"] > 0
    assert first["lower"] <= 1.0 <= first["upper"]


def test_model_metadata_is_built_with_brier_score_from_computed_metrics():
    # Catches notebooks serializing stale metrics or omitting Brier from the generated JSON.
    metrics = {
        "Acurácia": .827, "Precision": .3376, "Recall": .4344,
        "F1-score": .3799, "ROC-AUC": .7202, "Brier Score": .097714,
    }
    metadata = build_model_metadata(
        artifact_name="modelo_payflow_v1.joblib", algorithm="LogisticRegression",
        features=["idade", "score_credito"], sklearn_version="1.9.1", test_metrics=metrics,
    )
    assert metadata["metricas_teste"]["Brier Score"] == .0977
    assert metadata["threshold"] == .20
    assert metadata["features"] == ["idade", "score_credito"]


def test_model_metadata_rejects_missing_required_metric():
    with pytest.raises(ValueError, match="Brier Score"):
        build_model_metadata(
            artifact_name="modelo.joblib", algorithm="LogisticRegression", features=[],
            sklearn_version="1.9.1", test_metrics={"ROC-AUC": .72},
        )
