"""Build serializable metadata for the historical PayFlow model artifact."""

from __future__ import annotations


def build_model_metadata(*, artifact_name, algorithm, features, sklearn_version,
                         test_metrics, threshold=0.20, target="default_90d",
                         horizon_days=90, version="1.0.0") -> dict:
    """Create complete v1 metadata directly from computed evaluation metrics."""
    required_metrics = {"Acurácia", "Precision", "Recall", "F1-score", "ROC-AUC", "Brier Score"}
    missing = required_metrics.difference(test_metrics)
    if missing:
        raise ValueError(f"Missing required test metrics: {', '.join(sorted(missing))}")
    return {
        "versao_modelo": version,
        "arquivo_modelo": artifact_name,
        "algoritmo": algorithm,
        "threshold": float(threshold),
        "target": target,
        "horizonte_dias": int(horizon_days),
        "features": list(features),
        "versao_sklearn": sklearn_version,
        "metricas_teste": {name: round(float(value), 4) for name, value in test_metrics.items()},
    }
