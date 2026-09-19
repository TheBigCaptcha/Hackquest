from pathlib import Path
import pandas as pd

LABELS_PATH = Path("data/raw/elliptic_txs_classes.csv")

def load_transaction_labels(path: Path = LABELS_PATH) -> pd.DataFrame:
    """Load the local Elliptic transaction-label file without committing it to Git."""
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")
    df = pd.read_csv(path)
    required = {"txId", "class"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    df["txId"] = df["txId"].astype(str)
    return df
