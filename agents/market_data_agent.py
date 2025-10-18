"""Market Data Agent - Collects market data"""
from agents.base_agent import BaseAgent
from modules.data_fetcher import DataFetcher
from utils.helpers import *
import pandas as pd
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class MarketDataAgent(BaseAgent):
    def __init__(self):
        super().__init__("Market Data Agent", "market_data")
        self.data_fetcher = DataFetcher()

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        symbol = input_data.get('symbol')
        period = input_data.get('period', '1y')

        result = {
            'symbol': symbol,
            'price_data': {},
            'company_info': {},
            'news': [],
            'confidence': 0.0
        }

        # Get price data
        price_df = self.data_fetcher.get_stock_data(symbol, period)
        if price_df is not None and not price_df.empty:
            result['price_data'] = self._process_price_data(price_df)

        # Get company info
        result['company_info'] = self.data_fetcher.get_company_info(symbol)

        # Get news
        result['news'] = self.data_fetcher.get_news(symbol)[:10]

        # Confidence
        result['confidence'] = 0.8 if result['price_data'] else 0.3

        return result

    def _process_price_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        try:
            latest = df.iloc[-1]
            previous = df.iloc[-2] if len(df) > 1 else latest

            return {
                'current_price': float(latest['close']),
                'previous_close': float(previous['close']),
                'change_percent': float((latest['close'] - previous['close']) / previous['close'] * 100),
                'volume': int(latest['volume']) if 'volume' in latest else 0,
                'high_52w': float(df['high'].max()),
                'low_52w': float(df['low'].min())
            }
        except:
            return {}
