"""Risk Management Agent"""
from agents.base_agent import BaseAgent
from utils.helpers import *
import pandas as pd
import numpy as np
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class RiskAgent(BaseAgent):
    def __init__(self):
        super().__init__("Risk Agent", "risk")
        self.var_confidence = 0.95

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        price_data = input_data.get('price_data')

        if not price_data or not isinstance(price_data, dict):
            return {
                'risk_level': 'Unknown',
                'confidence': 0.0
            }

        # Calculate risk metrics
        volatility = price_data.get('volatility', 0)

        result = {
            'volatility': volatility,
            'risk_level': self._assess_risk_level(volatility),
            'var_95': self._estimate_var(volatility),
            'max_drawdown_estimate': -abs(volatility * 2),
            'confidence': 0.7
        }

        return result

    def _assess_risk_level(self, volatility: float) -> str:
        if volatility > 0.40:
            return 'High'
        elif volatility > 0.25:
            return 'Medium'
        return 'Low'

    def _estimate_var(self, volatility: float) -> float:
        # Simplified VaR estimation
        return -1.65 * volatility / np.sqrt(252)
