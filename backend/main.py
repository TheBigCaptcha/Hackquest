"""FastAPI entry point."""

from fastapi import FastAPI

app = FastAPI(title="Bitcoin Deanonymization API", description="SIH26146 transaction analysis and investigation prototype", version="0.1.0")

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}

@app.get("/api/transactions/sample")
def sample_transactions() -> dict:
    return {"transactions": [], "note": "Replace with the current mock/real transaction service."}
