"""Complementary, reproducible analyses using the development split only.

Run from the repository root with ``python -m src.experiments.complementary_analysis``.
The sole exception is the explicitly historical bootstrap interval, which only
quantifies uncertainty in the already published holdout evaluation and is never
used to choose a model, feature, or threshold.
"""

from __future__ import annotations

import hashlib
import json
import platform
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
from sklearn.base import clone
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline

from src.features.preprocessing import criar_preprocessador

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "raw" / "payflow_credit_risk.csv"
OUT = ROOT / "reports" / "experiments"
SEED = 42
THRESHOLD = 0.20
N_SPLITS = 5
N_BOOTSTRAP = 5000
TARGET = "default_90d"
FUTURE_FEATURES = ["parcelas_pagas_ate_3m", "atraso_primeira_parcela_dias"]
EXCLUDED = ["id_cliente", TARGET, *FUTURE_FEATURES, "status_apos_90d", "juros_mensal_pct"]


def brier_skill_score(y_true, probabilities, reference_prevalence: float) -> float:
    """BSS against a constant predictor set to training-set prevalence."""
    if not 0 <= reference_prevalence <= 1:
        raise ValueError("reference_prevalence must be between 0 and 1")
    reference = np.full(len(y_true), reference_prevalence, dtype=float)
    reference_brier = brier_score_loss(y_true, reference)
    if reference_brier == 0:
        return float("nan")
    return float(1 - brier_score_loss(y_true, probabilities) / reference_brier)


def bootstrap_metric_ci(y_true, values, *, metric: str, seed: int = SEED,
                        n_resamples: int = N_BOOTSTRAP, threshold: float = THRESHOLD) -> dict:
    """Paired row bootstrap; class-dependent metrics skip one-class resamples."""
    y = np.asarray(y_true, dtype=int)
    x = np.asarray(values, dtype=float)
    if y.shape[0] != x.shape[0] or y.ndim != 1:
        raise ValueError("y_true and values must be one-dimensional and equally sized")
    if metric not in {"roc_auc", "average_precision", "precision", "recall"}:
        raise ValueError(f"Unsupported metric: {metric}")
    rng = np.random.default_rng(seed)
    estimates = []
    skipped = 0
    for _ in range(n_resamples):
        indices = rng.integers(0, len(y), size=len(y))
        y_sample = y[indices]
        x_sample = x[indices]
        if metric in {"roc_auc", "average_precision"} and np.unique(y_sample).size < 2:
            skipped += 1
            continue
        prediction = (x_sample >= threshold).astype(int)
        if metric == "roc_auc":
            value = roc_auc_score(y_sample, x_sample)
        elif metric == "average_precision":
            value = average_precision_score(y_sample, x_sample)
        elif metric == "precision":
            value = precision_score(y_sample, prediction, zero_division=0)
        else:
            if y_sample.sum() == 0:
                skipped += 1
                continue
            value = recall_score(y_sample, prediction, zero_division=0)
        estimates.append(float(value))
    if not estimates:
        raise ValueError("No valid bootstrap resamples")
    lower, upper = np.quantile(estimates, [0.025, 0.975])
    return {
        "metric": metric,
        "estimate": float({
            "roc_auc": roc_auc_score,
            "average_precision": average_precision_score,
            "precision": lambda actual, predicted: precision_score(actual, predicted >= threshold, zero_division=0),
            "recall": lambda actual, predicted: recall_score(actual, predicted >= threshold, zero_division=0),
        }[metric](y, x)),
        "lower": float(lower),
        "upper": float(upper),
        "valid_resamples": len(estimates),
        "skipped_resamples": skipped,
        "seed": seed,
        "n_resamples": n_resamples,
        "method": "paired row bootstrap percentile interval",
    }


def _pipeline(X: pd.DataFrame, model=None) -> Pipeline:
    if model is None:
        model = LogisticRegression(max_iter=1000, random_state=SEED)
    return Pipeline([("preprocessing", criar_preprocessador(X)), ("model", model)])


def _development_split(df: pd.DataFrame):
    # Keep interest rate available for a separate availability-sensitive ablation.
    X = df.drop(columns=["id_cliente", TARGET, "status_apos_90d"])
    y = df[TARGET]
    X_dev, _, y_dev, _ = train_test_split(
        X, y, test_size=0.20, stratify=y, random_state=SEED
    )
    return X_dev, y_dev


def _oof(model, X, y, cv):
    probabilities = np.full(len(y), np.nan)
    baselines = np.full(len(y), np.nan)
    fold_rows = []
    for fold, (train_idx, valid_idx) in enumerate(cv.split(X, y), 1):
        fitted = clone(model).fit(X.iloc[train_idx], y.iloc[train_idx])
        pred_prob = fitted.predict_proba(X.iloc[valid_idx])[:, 1]
        prevalence = float(y.iloc[train_idx].mean())
        probabilities[valid_idx] = pred_prob
        baselines[valid_idx] = prevalence
        y_valid = y.iloc[valid_idx]
        fold_rows.append({
            "fold": fold,
            "roc_auc": roc_auc_score(y_valid, pred_prob),
            "average_precision": average_precision_score(y_valid, pred_prob),
            "brier": brier_score_loss(y_valid, pred_prob),
            "reference_prevalence_train": prevalence,
        })
    return probabilities, baselines, pd.DataFrame(fold_rows)


def _score_oof(label, y, probabilities, reference_probabilities, fold_rows, model_type, threshold=THRESHOLD):
    pred = (probabilities >= threshold).astype(int)
    reference_brier = brier_score_loss(y, reference_probabilities)
    return {
        "experimento": label,
        "modelo": model_type,
        "roc_auc_oof": roc_auc_score(y, probabilities),
        "roc_auc_media_folds": fold_rows["roc_auc"].mean(),
        "average_precision_oof": average_precision_score(y, probabilities),
        "prevalencia": float(y.mean()),
        "precision_oof_thr_020": precision_score(y, pred, zero_division=0),
        "recall_oof_thr_020": recall_score(y, pred, zero_division=0),
        "f1_oof_thr_020": f1_score(y, pred, zero_division=0),
        "brier_oof": brier_score_loss(y, probabilities),
        "brier_skill_score_oof": float(1 - brier_score_loss(y, probabilities) / reference_brier),
        "threshold": threshold,
        "roc_auc_dp_folds": fold_rows["roc_auc"].std(ddof=0),
    }


def _model_comparisons(X, y, cv):
    baseline_features = [col for col in X.columns if col not in {"juros_mensal_pct", *FUTURE_FEATURES}]
    variants = [
        ("Logistic Regression original", _pipeline(X[baseline_features]), baseline_features),
        ("Logistic Regression class_weight=balanced", _pipeline(X[baseline_features], LogisticRegression(max_iter=1000, random_state=SEED, class_weight="balanced")), baseline_features),
        ("Random Forest", _pipeline(X[baseline_features], RandomForestClassifier(n_estimators=200, min_samples_leaf=10, random_state=SEED, n_jobs=1)), baseline_features),
        ("Sem regiao", None, [col for col in baseline_features if col != "regiao"]),
        ("Sem regiao, idade e canal_aquisicao", None, [col for col in baseline_features if col not in {"regiao", "idade", "canal_aquisicao"}]),
        ("Com juros_mensal_pct (exploratorio)", None, [*baseline_features, "juros_mensal_pct"]),
    ]
    rows, oof_by_label, fold_by_label = [], {}, {}
    for label, model, columns in variants:
        model = _pipeline(X[columns]) if model is None else model
        pred, baseline, fold_rows = _oof(model, X[columns], y, cv)
        oof_by_label[label] = pred
        fold_by_label[label] = fold_rows
        rows.append(_score_oof(label, y, pred, baseline, fold_rows, type(model.named_steps["model"]).__name__))
    # Deliberately leaked analyses are isolated in this report and never candidates for use.
    for feature in FUTURE_FEATURES:
        columns = [*baseline_features, feature]
        label = f"COM LEAKAGE: {feature}"
        model = _pipeline(X[columns])
        pred, baseline, fold_rows = _oof(model, X[columns], y, cv)
        rows.append(_score_oof(label, y, pred, baseline, fold_rows, "LogisticRegression (didatico)"))
    columns = [*baseline_features, *FUTURE_FEATURES]
    label = "COM LEAKAGE: ambas as variaveis futuras"
    pred, baseline, fold_rows = _oof(_pipeline(X[columns]), X[columns], y, cv)
    rows.append(_score_oof(label, y, pred, baseline, fold_rows, "LogisticRegression (didatico)"))
    return pd.DataFrame(rows), oof_by_label, fold_by_label


def _fairness_groups(X, y, probabilities):
    rows = []
    groups = {
        "regiao": X["regiao"].astype(str),
        "canal_aquisicao": X["canal_aquisicao"].astype(str),
        "idade_faixa_quartil": pd.qcut(X["idade"], q=4, duplicates="drop").astype(str),
    }
    pred = (probabilities >= THRESHOLD).astype(int)
    for variable, labels in groups.items():
        for group in sorted(labels.unique()):
            mask = (labels.to_numpy() == group)
            target = np.asarray(y)[mask]
            prediction = pred[mask]
            n, positives, signals = len(target), int(target.sum()), int(prediction.sum())
            rows.append({
                "variavel": variable, "grupo": group, "n": n,
                "default_prevalencia": positives / n if n else np.nan,
                "taxa_sinalizacao": signals / n if n else np.nan,
                "recall": recall_score(target, prediction, zero_division=0) if positives else np.nan,
                "precision": precision_score(target, prediction, zero_division=0) if signals else np.nan,
                "suporte_suficiente_n_ge_30": n >= 30 and positives > 0 and signals > 0,
                "threshold": THRESHOLD,
            })
    return pd.DataFrame(rows)


def _historical_intervals(df, X, y):
    metadata = json.loads((ROOT / "models" / "modelo_payflow_v1.json").read_text(encoding="utf-8"))
    import joblib
    model = joblib.load(ROOT / "models" / metadata["arquivo_modelo"])
    _, indices_test = train_test_split(
        df.index, test_size=.20, stratify=df[TARGET], random_state=SEED
    )
    X_test = df.loc[indices_test, metadata["features"]]
    y_test = df.loc[indices_test, TARGET].to_numpy()
    probabilities = model.predict_proba(X_test)[:, 1]
    result = {
        "purpose": "quantify uncertainty of the already-consulted historical test only; not independent validation and not used for selection",
        "historical_test_rows": len(y_test),
        "historical_test_prevalence": float(y_test.mean()),
        "threshold": metadata["threshold"],
        "intervals": [bootstrap_metric_ci(y_test, probabilities, metric=m, seed=SEED, n_resamples=N_BOOTSTRAP)
                      for m in ["roc_auc", "precision", "recall"]],
        "baseline_metrics_recomputed": {
            "accuracy": accuracy_score(y_test, probabilities >= metadata["threshold"]),
            "precision": precision_score(y_test, probabilities >= metadata["threshold"]),
            "recall": recall_score(y_test, probabilities >= metadata["threshold"]),
            "roc_auc": roc_auc_score(y_test, probabilities),
            "brier": brier_score_loss(y_test, probabilities),
            "confusion_matrix": confusion_matrix(y_test, probabilities >= metadata["threshold"]).tolist(),
        },
    }
    return result


def run():
    df = pd.read_csv(DATA_PATH)
    X_dev, y_dev = _development_split(df)
    cv = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=SEED)
    comparisons, oof, folds = _model_comparisons(X_dev, y_dev, cv)
    OUT.mkdir(parents=True, exist_ok=True)
    comparisons.to_csv(OUT / "metricas_complementares_desenvolvimento.csv", index=False)

    # Keep fold-level paired differences visible; do not interpret them as equivalence tests.
    paired = []
    lr_folds = folds["Logistic Regression original"]
    rf_folds = folds["Random Forest"]
    for _, a in lr_folds.iterrows():
        b = rf_folds.loc[rf_folds.fold == a.fold].iloc[0]
        paired.append({"fold": int(a.fold), "roc_auc_lr": a.roc_auc, "roc_auc_rf": b.roc_auc,
                       "diferenca_lr_menos_rf": a.roc_auc - b.roc_auc,
                       "average_precision_lr": a.average_precision, "average_precision_rf": b.average_precision})
    pd.DataFrame(paired).to_csv(OUT / "diferencas_pareadas_folds.csv", index=False)
    fairness = _fairness_groups(X_dev.drop(columns="juros_mensal_pct"), y_dev, oof["Logistic Regression original"])
    fairness.to_csv(OUT / "analise_grupos_desenvolvimento.csv", index=False)
    correlation = df.loc[y_dev.index, ["juros_mensal_pct", "score_credito"]].corr(method="pearson").iloc[0, 1]
    correlation_result = {
        "pearson_r_juros_mensal_pct_score_credito": float(correlation),
        "development_rows": int(len(y_dev)),
        "interpretation": "Correlation is descriptive and does not establish the operational pricing sequence or causal mechanism.",
    }
    (OUT / "correlacao_juros_score.json").write_text(json.dumps(correlation_result, indent=2), encoding="utf-8")
    historical = _historical_intervals(df, X_dev, y_dev)
    (OUT / "intervalos_teste_historico.json").write_text(json.dumps(historical, indent=2), encoding="utf-8")

    metadata = {
        "dataset": "data/raw/payflow_credit_risk.csv",
        "dataset_sha256": hashlib.sha256(DATA_PATH.read_bytes()).hexdigest(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "development_rows": len(X_dev), "development_split": {"test_size": 0.20, "stratify": True, "random_state": SEED},
        "cv": {"name": "StratifiedKFold", "n_splits": N_SPLITS, "shuffle": True, "random_state": SEED},
        "threshold": THRESHOLD, "threshold_usage": "reporting only; retained historical operating point",
        "bootstrap": {"replicates": N_BOOTSTRAP, "seed": SEED, "interval": "percentile 95%", "historical_test_selection_use": False},
        "pr_auc": "Average Precision (sklearn average_precision_score), not trapezoidal PR-AUC",
        "brier_skill_score": "1 - Brier(model) / Brier(constant training prevalence); development OOF reference is fold-specific training prevalence",
        "model_selection_use_of_historical_test": False,
        "python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__, "scikit_learn": sklearn.__version__,
    }
    (OUT / "configuracao_analise_complementar.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    print(comparisons.to_string(index=False, float_format=lambda value: f"{value:.6f}"))
    print("\nHistorical test confidence intervals (uncertainty only):")
    print(json.dumps(historical, indent=2))
    print("\nDevelopment fairness groups:")
    print(fairness.to_string(index=False, float_format=lambda value: f"{value:.6f}"))


if __name__ == "__main__":
    run()
