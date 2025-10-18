"""API Schemas for validation"""
from typing import Dict, Any

ANALYZE_SCHEMA = {
    "type": "object",
    "properties": {
        "symbol": {"type": "string"},
        "period": {"type": "string", "enum": ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y"]},
        "analysis_type": {"type": "string", "enum": ["quick", "comprehensive"]}
    },
    "required": ["symbol"]
}

PORTFOLIO_SCHEMA = {
    "type": "object",
    "properties": {
        "holdings": {"type": "object"}
    }
}