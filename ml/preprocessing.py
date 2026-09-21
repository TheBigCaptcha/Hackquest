"""
preprocessing.py
----------------
Loads the raw Elliptic Bitcoin dataset, merges features with labels,
and produces a temporal train/test split.

Expected input files (edit DATA_DIR to point at them):
    elliptic_txs_features.csv
    elliptic_txs_classes.csv
    elliptic_txs_edgelist.csv
"""
import pandas as pd

DATA_DIR = "data/elliptic_bitcoin_dataset"   # <-- change if your data lives elsewhere
TRAIN_MAX_STEP = 34                          # steps 1-34 = train, 35-49 = test

# Column names for the features file (it ships with no header).
# col 0 = txId, col 1 = time_step, cols 2-94 = 93 "local" features,
# cols 95-166 = 72 "aggregated" (1-hop neighbourhood) features.
FEATURE_COLUMNS = (
    ["txId", "time_step"]
    + [f"local_{i}" for i in range(1, 94)]
    + [f"agg_{i}" for i in range(1, 73)]
)
FEATURE_NAMES = [c for c in FEATURE_COLUMNS if c not in ("txId", "time_step")]


def load_raw(data_dir: str = DATA_DIR):
    """Load the three raw CSVs."""
    features = pd.read_csv(f"{data_dir}/elliptic_txs_features.csv", header=None)
    features.columns = FEATURE_COLUMNS

    classes = pd.read_csv(f"{data_dir}/elliptic_txs_classes.csv")
    edges = pd.read_csv(f"{data_dir}/elliptic_txs_edgelist.csv")

    return features, classes, edges


def merge_and_label(features: pd.DataFrame, classes: pd.DataFrame) -> pd.DataFrame:
    """Join features with classes and map class -> numeric label.

    Label convention: 1 = illicit, 0 = licit, -1 = unknown (unlabeled).
    """
    df = features.merge(classes, on="txId", how="left")
    df["label"] = df["class"].map({"1": 1, "2": 0, "unknown": -1})
    return df


def temporal_split(df: pd.DataFrame, train_max_step: int = TRAIN_MAX_STEP):
    """Split LABELED transactions into train/test by time step (not randomly).

    A random split would leak future network structure into training and
    overstate performance. Training on the past and testing on the future
    mirrors how the model is actually used.

    Returns X_train, y_train, X_test, y_test, unknown_df
    """
    labeled = df[df.label != -1].copy()
    unknown = df[df.label == -1].copy()

    train_df = labeled[labeled.time_step <= train_max_step]
    test_df = labeled[labeled.time_step > train_max_step]

    X_train, y_train = train_df[FEATURE_NAMES], train_df["label"]
    X_test, y_test = test_df[FEATURE_NAMES], test_df["label"]

    return X_train, y_train, X_test, y_test, unknown


def load_and_split(data_dir: str = DATA_DIR, train_max_step: int = TRAIN_MAX_STEP):
    """Convenience wrapper: raw files -> ready-to-train split, in one call."""
    features, classes, _edges = load_raw(data_dir)
    df = merge_and_label(features, classes)
    return temporal_split(df, train_max_step)


if __name__ == "__main__":
    X_train, y_train, X_test, y_test, unknown = load_and_split()
    print(f"Train: {len(X_train):,} txs, illicit rate {y_train.mean():.2%}")
    print(f"Test:  {len(X_test):,} txs, illicit rate {y_test.mean():.2%}")
    print(f"Unknown (unlabeled): {len(unknown):,} txs")
