"""
predict.py
----------
Loads the model saved by train.py (no retraining) and scores transactions,
producing the txId -> risk_probability -> suspicious_indicators output
that gets handed to the graph/risk-scoring side of the pipeline.

Run: python predict.py
Produces: scored_test_transactions.csv, scored_unknown_transactions.csv
"""
import joblib
import numpy as np
import pandas as pd

from preprocessing import load_and_split

MODEL_PATH = "model.pkl"
TOP_N_INDICATORS = 5   # how many top-importance features to attach as indicators
THRESHOLD = 0.5


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
    test_scored.to_csv("scored_test_transactions.csv", index=False)
    print(f"Scored {len(test_scored):,} labeled test transactions -> scored_test_transactions.csv")

    # Score UNKNOWN transactions -> the real deliverable for the graph team
    X_unknown = unknown[X_train.columns]
    unknown_scored = build_scored_output(unknown, X_unknown, model, top_features)
    unknown_scored.to_csv("scored_unknown_transactions.csv", index=False)
    print(f"Scored {len(unknown_scored):,} unknown transactions -> scored_unknown_transactions.csv")

    n_flagged = (unknown_scored.predicted_label == "suspicious").sum()
    print(f"{n_flagged:,}/{len(unknown_scored):,} ({n_flagged/len(unknown_scored):.1%}) flagged suspicious")


if __name__ == "__main__":
    main()
