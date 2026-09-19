CREATE TABLE entity_risk_scores (
    entity_id VARCHAR(64) PRIMARY KEY,
    risk_score FLOAT NOT NULL CHECK (risk_score >= 0 AND risk_score <= 100),
    risk_level VARCHAR(16) NOT NULL,
    model_version VARCHAR(32) NOT NULL,
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
