MOCK_ENTITIES = {
    "cluster_123": {
        "entity_id": "cluster_123",
        "entity_type": "Cluster",
        "risk_score": 88.5,
        "risk_level": "HIGH",
        "relevant_indicators": [
            "Rapid succession transfers (< 5 mins)",
            "High connectivity to previously flagged entity",
            "Unusual off-hours transaction velocity",
        ],
        "metrics": {
            "total_transactions": 142,
            "suspicious_transactions": 19,
            "connection_count": 8,
        },
    }
}


MOCK_TRANSACTIONS = {
    "cluster_123": [
        {
            "transaction_id": "tx_9001",
            "source_entity": "acc_A",
            "target_entity": "acc_B",
            "amount": 12500.00,
            "timestamp": "2026-09-15T14:32:00Z",
            "is_suspicious": True,
            "flag_reason": "Structured deposit pattern",
        },
        {
            "transaction_id": "tx_9002",
            "source_entity": "acc_B",
            "target_entity": "acc_C",
            "amount": 12450.00,
            "timestamp": "2026-09-15T14:34:10Z",
            "is_suspicious": True,
            "flag_reason": "Rapid pass-through funds",
        },
        {
            "transaction_id": "tx_9003",
            "source_entity": "acc_A",
            "target_entity": "acc_D",
            "amount": 150.00,
            "timestamp": "2026-09-16T09:10:00Z",
            "is_suspicious": False,
            "flag_reason": None,
        },
    ]
}


MOCK_NETWORKS = {
    "cluster_123": {
        "nodes": [
            {
                "id": "acc_A",
                "label": "Account A",
                "node_type": "origin",
            },
            {
                "id": "acc_B",
                "label": "Account B",
                "node_type": "intermediate",
            },
            {
                "id": "acc_C",
                "label": "Account C",
                "node_type": "connected",
            },
            {
                "id": "acc_D",
                "label": "Account D",
                "node_type": "account",
            },
        ],
        "edges": [
            {
                "source": "acc_A",
                "target": "acc_B",
                "amount": 12500.00,
                "weight": 0.9,
            },
            {
                "source": "acc_B",
                "target": "acc_C",
                "amount": 12450.00,
                "weight": 0.95,
            },
            {
                "source": "acc_A",
                "target": "acc_D",
                "amount": 150.00,
                "weight": 0.1,
            },
        ],
    }
}
