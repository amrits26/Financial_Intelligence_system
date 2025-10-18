"""Fundamental Analysis Agent"""
from agents.base_agent import BaseAgent
from typing import Dict, Any

class FundamentalAgent(BaseAgent):
    def __init__(self):
        super().__init__("Fundamental Agent", "fundamental")

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        company_info = input_data.get('company_info', {})

        return {
            'pe_ratio': company_info.get('pe_ratio'),
            'market_cap': company_info.get('market_cap'),
            'valuation': 'Fair' if company_info.get('pe_ratio', 0) < 25 else 'Expensive',
            'confidence': 0.6
        }
