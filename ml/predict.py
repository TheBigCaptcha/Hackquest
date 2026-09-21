"""
predict.py
----------
Loads the model saved by train.py (no retraining) and scores transactions,
producing the txId -> risk_probability -> suspicious_indicators output
that gets handed to the graph/risk-scoring side of the pipeline, PLUS a
predictions.csv in the exact schema the API/app side expects:
    transaction_id, risk_score (0-100), risk_level (LOW/MEDIUM/HIGH/CRITICAL)

Run: python predict.py
Produces (written next to this script, i.e. in ml/ regardless of cwd):
    predictions.csv                  <- what the app/API teammate consumes
    scored_test_transactions.csv     <- labeled test set, for validation
    scored_unknown_transactions.csv  <- full detail version, for the graph team
"""
import os

import joblib
import numpy as np
import pandas as pd

from preprocessing import load_and_split

# Resolve paths relative to this file, so output always lands in ml/
# even if the script is run from the repo root (e.g. `python ml/predict.py`).
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(SCRIPT_DIR, "model.pkl")
PREDICTIONS_PATH = os.path.join(SCRIPT_DIR, "predictions.csv")
TEST_SCORED_PATH = os.path.join(SCRIPT_DIR, "scored_test_transactions.csv")
UNKNOWN_SCORED_PATH = os.path.join(SCRIPT_DIR, "scored_unknown_transactions.csv")

TOP_N_INDICATORS = 5   # how many top-importance features to attach as indicators
THRESHOLD = 0.5


def risk_level(score_0_100: np.ndarray) -> np.ndarray:
    """Bucket a 0-100 risk score into LOW/MEDIUM/HIGH/CRITICAL."""
    return np.select(
        [score_0_100 >= 75, score_0_100 >= 50, score_0_100 >= 25],
        ["CRITICAL", "HIGH", "MEDIUM"],
        default="LOW",
    )


def build_scored_output(frame: pd.DataFrame, X: pd.DataFrame, model, top_features: list) -> pd.DataFrame:
    """Score a set of transactions and attach indicator columns."""
    proba = model.predict_proba(X)[:, 1]
    pred = (proba >= THRESHOLD).astype(int)

    out = pd.DataFrame(
        {
            "txId": frame["txId"].values,
            "time_step": frame["time_step"].values,
            "risk_probability": proba,
            "predicted_label": np.where(pred == 1, "suspicious", "licit"),
        }
    )
    for feat in top_features:
        out[f"indicator_{feat}"] = X[feat].values

    return out.sort_values("risk_probability", ascending=False)


def main():
    model = joblib.load(MODEL_PATH)

    X_train, y_train, X_test, y_test, unknown = load_and_split()

    # Reconstruct the labeled test frame (txId, time_step) to attach to scores.
    # (load_and_split only returns X/y, so we re-derive the frame here.)
    from preprocessing import load_raw, merge_and_label, TRAIN_MAX_STEP

    features, classes, _edges = load_raw()
    df = merge_and_label(features, classes)
    labeled = df[df.label != -1]
    test_df = labeled[labeled.time_step > TRAIN_MAX_STEP]

    top_features = (
        pd.Series(model.feature_importances_, index=X_train.columns)
        .sort_values(ascending=False)
        .head(TOP_N_INDICATORS)
        .index.tolist()
    )

    # Score labeled test transactions (useful to sanity-check against ground truth)
    test_scored = build_scored_output(test_df, X_test, model, top_features)
    test_scored["true_label"] = np.where(y_test.values == 1, "illicit", "licit")
    test_scored.to_csv(TEST_SCORED_PATH, index=False)
    print(f"Scored {len(test_scored):,} labeled test transactions -> {TEST_SCORED_PATH}")

    # Score UNKNOWN transactions -> detailed version for the graph team
    X_unknown = unknown[X_train.columns]
    unknown_scored = build_scored_output(unknown, X_unknown, model, top_features)
    unknown_scored.to_csv(UNKNOWN_SCORED_PATH, index=False)
    print(f"Scored {len(unknown_scored):,} unknown transactions -> {UNKNOWN_SCORED_PATH}")

    n_flagged = (unknown_scored.predicted_label == "suspicious").sum()
    print(f"{n_flagged:,}/{len(unknown_scored):,} ({n_flagged/len(unknown_scored):.1%}) flagged suspicious")

    # ------------------------------------------------------------------
    # predictions.csv -- the exact schema the API/app teammate is expecting:
    # transaction_id, risk_score (0-100), risk_level (LOW/MEDIUM/HIGH/CRITICAL)
    # Covers every transaction we can score (labeled test set + unknown),
    # so any transaction_id the app looks up has a row.
    # ------------------------------------------------------------------
    combined = pd.concat(
        [
            test_scored[["txId", "risk_probability"]],
            unknown_scored[["txId", "risk_probability"]],
        ],
        ignore_index=True,
    )
    combined["risk_score"] = (combined["risk_probability"] * 100).round(1)
    combined["risk_level"] = risk_level(combined["risk_score"].values)

    predictions = combined.rename(columns={"txId": "transaction_id"})[
        ["transaction_id", "risk_score", "risk_level"]
    ].sort_values("risk_score", ascending=False)

    predictions.to_csv(PREDICTIONS_PATH, index=False)
    print(f"\nWrote {len(predictions):,} rows -> {PREDICTIONS_PATH}")
    print(predictions["risk_level"].value_counts())


if __name__ == "__main__":
    main()
