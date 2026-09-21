"""
train.py
--------
Trains the Random Forest baseline on the Elliptic dataset, evaluates it
with imbalance-aware metrics, and saves the fitted model + feature
importances to disk for predict.py to reuse (no retraining needed there).

Run: python train.py
Produces: model.pkl, feature_importances.csv, summary_metrics.json
"""
import json

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from preprocessing import FEATURE_NAMES, load_and_split

RANDOM_STATE = 42
MODEL_PATH = "model.pkl"


def train_model(X_train, y_train) -> RandomForestClassifier:
    model = RandomForestClassifier(
        n_estimators=300,
        min_samples_leaf=2,
        class_weight="balanced_subsample",  # addresses class imbalance
        n_jobs=-1,
        random_state=RANDOM_STATE,
    )
    model.fit(X_train, y_train)
    return model


def evaluate(model, X_test, y_test) -> dict:
    y_proba = model.predict_proba(X_test)[:, 1]
    y_pred = model.predict(X_test)

    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_proba)
    pr_auc = average_precision_score(y_test, y_proba)  # robust to imbalance
    cm = confusion_matrix(y_test, y_pred)

    print(f"Precision (illicit): {precision:.4f}")
    print(f"Recall (illicit):    {recall:.4f}")
    print(f"F1-score (illicit):  {f1:.4f}")
    print(f"ROC-AUC:             {roc_auc:.4f}")
    print(f"PR-AUC:              {pr_auc:.4f}")
    print("\nConfusion matrix [rows=true, cols=pred] (0=licit,1=illicit):")
    print(cm)
    print("\n" + classification_report(y_test, y_pred, target_names=["licit", "illicit"], digits=4))

    # Threshold sweep: illicit is rare and costly to miss, so it's worth
    # showing the precision/recall trade-off instead of only the 0.5 default.
    print("Precision/Recall at alternative thresholds:")
    for t in [0.3, 0.4, 0.5, 0.6, 0.7]:
        yp = (y_proba >= t).astype(int)
        p = precision_score(y_test, yp, zero_division=0)
        r = recall_score(y_test, yp, zero_division=0)
        f = f1_score(y_test, yp, zero_division=0)
        print(f"  t={t:.1f} -> precision={p:.3f}  recall={r:.3f}  f1={f:.3f}  flagged={yp.sum()}")

    return {
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "roc_auc": float(roc_auc),
        "pr_auc": float(pr_auc),
        "confusion_matrix": cm.tolist(),
    }


def main():
    X_train, y_train, X_test, y_test, _unknown = load_and_split()
    print(f"Train: {len(X_train):,} txs (illicit rate {y_train.mean():.2%})")
    print(f"Test:  {len(X_test):,} txs (illicit rate {y_test.mean():.2%})\n")

    model = train_model(X_train, y_train)
    metrics = evaluate(model, X_test, y_test)

    # Save the fitted model so predict.py doesn't need to retrain.
    joblib.dump(model, MODEL_PATH)
    print(f"\nModel saved to {MODEL_PATH}")

    # Feature importances -> which features drive "suspicious" predictions.
    importances = (
        pd.Series(model.feature_importances_, index=FEATURE_NAMES)
        .sort_values(ascending=False)
    )
    importances.to_csv("feature_importances.csv", header=["importance"])
    print("Top 10 features:")
    print(importances.head(10))

    with open("summary_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)


if __name__ == "__main__":
    main()
