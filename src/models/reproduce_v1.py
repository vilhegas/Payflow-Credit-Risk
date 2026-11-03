"""Deterministically rebuild the historical v1 artifacts outside ``models/``.

Example from the repository root::

    python -m src.models.reproduce_v1 --output-dir reports/reproduced_v1

The output directory must not already contain either artifact. This keeps the
versioned baseline safe while providing a clean-clone reproduction procedure.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import pandas as pd
import sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from src.features.preprocessing import criar_preprocessador
from src.models.metadata import build_model_metadata

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "raw" / "payflow_credit_risk.csv"
METADATA_PATH = ROOT / "models" / "modelo_payflow_v1.json"
def reproduce_v1_artifacts(output_dir: str | Path) -> tuple[Path, Path]:
    """Fit v1 on the fixed development split and save model plus metadata."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = output_dir / "modelo_payflow_v1.joblib"
    metadata_path = output_dir / "modelo_payflow_v1.json"
    if artifact_path.exists() or metadata_path.exists():
        raise FileExistsError(f"Refusing to overwrite v1 output in {output_dir}")

    historical_metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    df = pd.read_csv(DATA_PATH)
    features = historical_metadata["features"]
    X, y = df[features], df[historical_metadata["target"]]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, stratify=y, random_state=42
    )
    model = Pipeline([
        ("preprocessamento", criar_preprocessador(X_train)),
        ("modelo", LogisticRegression(max_iter=1000, random_state=42)),
    ])
    model.fit(X_train, y_train)
    probabilities = model.predict_proba(X_test)[:, 1]
    predictions = (probabilities >= historical_metadata["threshold"]).astype(int)
    metrics = {
        "Acurácia": accuracy_score(y_test, predictions),
        "Precision": precision_score(y_test, predictions, zero_division=0),
        "Recall": recall_score(y_test, predictions, zero_division=0),
        "F1-score": f1_score(y_test, predictions, zero_division=0),
        "ROC-AUC": roc_auc_score(y_test, probabilities),
        "Brier Score": brier_score_loss(y_test, probabilities),
    }
    metadata = build_model_metadata(
        artifact_name=artifact_path.name,
        algorithm=model.named_steps["modelo"].__class__.__name__,
        features=features,
        sklearn_version=sklearn.__version__,
        test_metrics=metrics,
        threshold=historical_metadata["threshold"],
        target=historical_metadata["target"],
        horizon_days=historical_metadata["horizonte_dias"],
        version=historical_metadata["versao_modelo"],
    )
    joblib.dump(model, artifact_path)
    metadata_path.write_text(json.dumps(metadata, indent=4, ensure_ascii=False), encoding="utf-8")
    return artifact_path, metadata_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, help="Diretório novo ou vazio fora de models/")
    args = parser.parse_args()
    artifact_path, metadata_path = reproduce_v1_artifacts(args.output_dir)
    print(f"Modelo reproduzido: {artifact_path}")
    print(f"Metadados reproduzidos: {metadata_path}")


if __name__ == "__main__":
    main()
