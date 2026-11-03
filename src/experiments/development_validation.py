"""Reproducible development-only experiments for PayFlow Credit Risk.

Run from the repository root with:
    python -m src.experiments.development_validation

All reported comparisons use only the 4,000-row stratified development split.
The held-out partition is discarded and never enters experiment calculations.
"""

from __future__ import annotations

import json
import hashlib
import platform
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_predict, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.utils.validation import check_is_fitted

from src.features.preprocessing import criar_preprocessador


ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "raw" / "payflow_credit_risk.csv"
OUTPUT_DIR = ROOT / "reports" / "experiments"
EXCLUDED = [
    "id_cliente",
    "default_90d",
    "parcelas_pagas_ate_3m",
    "atraso_primeira_parcela_dias",
    "status_apos_90d",
    "juros_mensal_pct",
]
SEED = 42
N_SPLITS = 5
THRESHOLDS = [0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50]
FP_FN_COSTS = {
    "FP=FN (1:1)": (1, 1),
    "FN=3x FP (1:3)": (1, 3),
    "FP=3x FN (3:1)": (3, 1),
    "FN=5x FP (1:5)": (1, 5),
}


class EmploymentGroupMedianImputer(BaseEstimator, TransformerMixin):
    """Impute missing employment duration using development-fold group medians."""

    def fit(self, X: pd.DataFrame, y=None):
        if not isinstance(X, pd.DataFrame) or "autonomo" not in X or "tempo_emprego_anos" not in X:
            raise ValueError("Expected a DataFrame with autonomo and tempo_emprego_anos columns.")
        self.overall_median_ = float(X["tempo_emprego_anos"].median())
        self.group_medians_ = X.groupby("autonomo", observed=True)["tempo_emprego_anos"].median().to_dict()
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        check_is_fitted(self, ["overall_median_", "group_medians_"])
        result = X.copy()
        missing = result["tempo_emprego_anos"].isna()
        result.loc[missing, "tempo_emprego_anos"] = result.loc[missing, "autonomo"].map(self.group_medians_)
        result["tempo_emprego_anos"] = result["tempo_emprego_anos"].fillna(self.overall_median_)
        return result


def _load_development_data():
    df = pd.read_csv(DATA_PATH)
    X = df.drop(columns=EXCLUDED)
    y = df["default_90d"]
    X_dev, _, y_dev, _ = train_test_split(
        X, y, test_size=0.20, random_state=SEED, stratify=y
    )
    return X_dev, y_dev


def _pipeline(strategy: str, X: pd.DataFrame) -> Pipeline:
    steps = []
    if strategy == "median_group_employment":
        steps.append(("employment_group_imputation", EmploymentGroupMedianImputer()))
    steps.extend([
        ("preprocessing", criar_preprocessador(
            X, use_missing_indicator=(strategy == "median_with_indicators")
        )),
        ("model", LogisticRegression(max_iter=1000, random_state=SEED)),
    ])
    return Pipeline(steps)


def run_imputation_experiments(X: pd.DataFrame, y: pd.Series) -> pd.DataFrame:
    cv = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=SEED)
    strategies = {
        "median_original": "Mediana global (baseline)",
        "median_with_indicators": "Mediana + indicadores de ausência",
        "median_group_employment": "Mediana por grupo em tempo de emprego",
    }
    rows = []
    reference_oof = None
    for key, label in strategies.items():
        model = _pipeline(key, X)
        fold_scores = cross_validate(model, X, y, cv=cv, scoring="roc_auc", n_jobs=1)["test_score"]
        oof = cross_val_predict(model, X, y, cv=cv, method="predict_proba", n_jobs=1)[:, 1]
        pred = (oof >= 0.20).astype(int)
        rows.append({
            "estrategia": label,
            "roc_auc_media_folds": float(fold_scores.mean()),
            "roc_auc_dp_folds": float(fold_scores.std()),
            "roc_auc_oof_agregada": float(roc_auc_score(y, oof)),
            "precision_oof_thr_020": float(precision_score(y, pred, zero_division=0)),
            "recall_oof_thr_020": float(recall_score(y, pred, zero_division=0)),
            "f1_oof_thr_020": float(f1_score(y, pred, zero_division=0)),
            "brier_oof": float(brier_score_loss(y, oof)),
            "diferenca_auc_media_vs_baseline": 0.0,
            "diferenca_auc_oof_vs_baseline": 0.0,
            "diferenca_precision_oof_thr_020_vs_baseline": 0.0,
            "diferenca_recall_oof_thr_020_vs_baseline": 0.0,
            "diferenca_f1_oof_thr_020_vs_baseline": 0.0,
            "diferenca_brier_oof_vs_baseline": 0.0,
        })
        if reference_oof is None:
            reference_oof = (float(fold_scores.mean()), float(roc_auc_score(y, oof)))
        else:
            rows[-1]["diferenca_auc_media_vs_baseline"] = float(fold_scores.mean() - reference_oof[0])
            rows[-1]["diferenca_auc_oof_vs_baseline"] = float(roc_auc_score(y, oof) - reference_oof[1])
    delta_metrics = [
        "precision_oof_thr_020",
        "recall_oof_thr_020",
        "f1_oof_thr_020",
        "brier_oof",
    ]
    baseline = rows[0]
    for row in rows[1:]:
        for metric in delta_metrics:
            row[f"diferenca_{metric}_vs_baseline"] = row[metric] - baseline[metric]
    return pd.DataFrame(rows)


def run_threshold_experiment(X: pd.DataFrame, y: pd.Series) -> pd.DataFrame:
    cv = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=SEED)
    model = _pipeline("median_original", X)
    oof = cross_val_predict(model, X, y, cv=cv, method="predict_proba", n_jobs=1)[:, 1]
    rows = []
    for threshold in THRESHOLDS:
        pred = (oof >= threshold).astype(int)
        tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
        row = {
            "threshold": threshold,
            "TP": int(tp), "TN": int(tn), "FP": int(fp), "FN": int(fn),
            "precision": float(precision_score(y, pred, zero_division=0)),
            "recall": float(recall_score(y, pred, zero_division=0)),
            "f1": float(f1_score(y, pred, zero_division=0)),
        }
        for label, (fp_cost, fn_cost) in FP_FN_COSTS.items():
            row[f"custo_{label}"] = int(fp * fp_cost + fn * fn_cost)
        rows.append(row)
    return pd.DataFrame(rows)


def main():
    X_dev, y_dev = _load_development_data()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    imputations = run_imputation_experiments(X_dev, y_dev)
    thresholds = run_threshold_experiment(X_dev, y_dev)
    imputations.to_csv(OUTPUT_DIR / "comparacao_imputacao.csv", index=False)
    thresholds.to_csv(OUTPUT_DIR / "sensibilidade_thresholds.csv", index=False)
    metadata = {
        "dataset": "data/raw/payflow_credit_risk.csv",
        "dataset_sha256": hashlib.sha256(DATA_PATH.read_bytes()).hexdigest(),
        "experiment_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "development_rows": int(len(X_dev)),
        "development_split": {"test_size": 0.20, "stratify": True, "random_state": SEED},
        "cv": {"class": "StratifiedKFold", "n_splits": N_SPLITS, "shuffle": True, "random_state": SEED},
        "estimator": "LogisticRegression(max_iter=1000, random_state=42)",
        "threshold_metrics": "out-of-fold development predictions; classification threshold 0.20 for imputation metrics",
        "threshold_costs": FP_FN_COSTS,
        "python_version": platform.python_version(),
        "python_packages": {"pandas": pd.__version__, "numpy": np.__version__, "scikit_learn": sklearn.__version__},
        "test_split_used_for_selection": False,
    }
    (OUTPUT_DIR / "configuracao.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    print("Development rows:", len(X_dev))
    print("\nImputation comparison:")
    print(imputations.to_string(index=False, float_format=lambda value: f"{value:.6f}"))
    print("\nThreshold sensitivity:")
    print(thresholds.to_string(index=False, float_format=lambda value: f"{value:.6f}"))
    print("\nSaved: reports/experiments/comparacao_imputacao.csv, sensibilidade_thresholds.csv, configuracao.json")


if __name__ == "__main__":
    main()
