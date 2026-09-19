from pathlib import Path
from typing import Optional

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from schemas import (
    EntityDetailResponse,
    EntityMetrics,
    NetworkEdge,
    NetworkGraph,
    NetworkNode,
    RiskLevel,
    SearchResultItem,
    Transaction,
)

DATA_PATH = Path("data/raw/elliptic_txs_classes.csv")

app = FastAPI(
    title="Financial Anomaly & Entity Investigation API",
    description="Backend bridge connecting Bitcoin/ML analysis outputs to the investigation frontend.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_labels() -> pd.DataFrame:
    if not DATA_PATH.exists():
        return pd.DataFrame(columns=["txId", "class"])
    df = pd.read_csv(DATA_PATH)
    df["txId"] = df["txId"].astype(str)
    return df


def class_to_suspicious(value: str) -> bool:
    # Elliptic labels: 1 = illicit, 2 = licit, unknown = unlabeled.
    return str(value) == "1"


@app.get("/", tags=["Health Check"])
def health_check():
    labels = load_labels()
    return {
        "status": "online",
        "message": "Investigation API is running.",
        "labels_loaded": not labels.empty,
        "label_rows": len(labels),
    }


@app.get("/api/dataset/summary", tags=["Dataset"])
def dataset_summary():
    labels = load_labels()
    if labels.empty:
        return {
            "loaded": False,
            "message": "Place elliptic_txs_classes.csv in data/raw/ locally.",
        }

    counts = labels["class"].value_counts().to_dict()
    return {
        "loaded": True,
        "total_transactions": len(labels),
        "illicit_labeled": int(counts.get("1", 0)),
        "licit_labeled": int(counts.get("2", 0)),
        "unknown": int(counts.get("unknown", 0)),
    }


@app.get("/api/entities/search", response_model=list[SearchResultItem], tags=["Entities"])
def search_entities(
    query: str = Query(..., min_length=1, description="Transaction ID search query")
):
    labels = load_labels()
    if labels.empty:
        return []

    matches = labels[labels["txId"].str.contains(query, case=False, na=False)].head(50)
    results = []
    for _, row in matches.iterrows():
        results.append(
            SearchResultItem(
                entity_id=f"tx_{row['txId']}",
                risk_score=None,
                risk_level=RiskLevel.UNASSESSED,
            )
        )
    return results


@app.get("/api/transactions/{transaction_id}", response_model=Transaction, tags=["Transactions"])
def get_transaction(transaction_id: str):
    tx_id = transaction_id.removeprefix("tx_")
    labels = load_labels()
    if labels.empty:
        raise HTTPException(status_code=503, detail="Elliptic labels dataset is not loaded.")

    match = labels[labels["txId"] == tx_id]
    if match.empty:
        raise HTTPException(status_code=404, detail=f"Transaction '{transaction_id}' not found.")

    row = match.iloc[0]
    suspicious = class_to_suspicious(row["class"])
    return Transaction(
        transaction_id=tx_id,
        source_entity="unknown",
        target_entity="unknown",
        is_suspicious=suspicious,
        flag_reason="Elliptic class=1 (illicit label)" if suspicious else None,
    )


@app.get("/api/transactions", tags=["Transactions"])
def list_transactions(
    suspicious_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=500),
):
    labels = load_labels()
    if labels.empty:
        return []

    if suspicious_only:
        labels = labels[labels["class"].map(class_to_suspicious)]

    return [
        {
            "transaction_id": str(row.txId),
            "label": str(row["class"]),
            "is_suspicious": class_to_suspicious(row["class"]),
        }
        for row in labels.head(limit).itertuples()
    ]


@app.get(
    "/api/entities/{entity_id}/network",
    response_model=NetworkGraph,
    tags=["Graph & Network"],
)
def get_entity_network(entity_id: str):
    raise HTTPException(
        status_code=501,
        detail="Graph data is not loaded yet. Add the Elliptic edge list and connect graph_builder.py.",
    )
