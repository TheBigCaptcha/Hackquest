"""Pydantic models shared by the investigation API.

Keep API contracts here so endpoint implementations do not duplicate
request/response model definitions.
"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNASSESSED = "UNASSESSED"


class Transaction(BaseModel):
    transaction_id: str
    source_entity: str
    target_entity: str
    amount: Optional[float] = None
    timestamp: Optional[str] = None
    is_suspicious: bool
    flag_reason: Optional[str] = None


class NetworkNode(BaseModel):
    id: str
    label: str
    node_type: str
    risk_score: Optional[float] = Field(None, ge=0.0, le=100.0)


class NetworkEdge(BaseModel):
    id: str
    source: str
    target: str
    amount: Optional[float] = None
    weight: float = 0.0
    is_suspicious: bool = False
    timestamp: Optional[str] = None


class NetworkGraph(BaseModel):
    nodes: List[NetworkNode]
    edges: List[NetworkEdge]


class EntityMetrics(BaseModel):
    total_transactions: int
    suspicious_transactions: int
    connection_count: int


class EntityDetailResponse(BaseModel):
    entity_id: str
    entity_type: str
    risk_score: float = Field(..., ge=0.0, le=100.0)
    risk_level: RiskLevel
    relevant_indicators: List[str]
    metrics: EntityMetrics


class SearchResultItem(BaseModel):
    entity_id: str
    risk_score: Optional[float] = None
    risk_level: RiskLevel
