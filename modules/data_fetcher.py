"""
Data Fetcher Module
Handles fetching financial data from multiple APIs
"""
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import logging
from config.settings import Config

logger = logging.getLogger(__name__)

class DataFetcher:
    """Fetches financial data from multiple sources"""

    def __init__(self):
        self.alpha_vantage_key = Config.ALPHA_VANTAGE_API_KEY
        self.finnhub_key = Config.FINNHUB_API_KEY

    def get_stock_data(self, symbol: str, period: str = '1y') -> Optional[pd.DataFrame]:
        """
        Get stock price data

        Args:
            symbol: Stock ticker symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)

        Returns:
            DataFrame with OHLCV data
        """
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period)

            if df.empty:
                logger.warning(f"No data found for {symbol}")
                return None

            # Standardize column names
            df.columns = [col.lower() for col in df.columns]

            logger.info(f"Fetched {len(df)} days of data for {symbol}")
            return df

        except Exception as e:
            logger.error(f"Error fetching stock data for {symbol}: {e}")
            return None

    def get_company_info(self, symbol: str) -> Dict[str, Any]:
        """Get company fundamental information"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            # Extract key metrics
            company_data = {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', None),
                'forward_pe': info.get('forwardPE', None),
                'peg_ratio': info.get('pegRatio', None),
                'price_to_book': info.get('priceToBook', None),
                'dividend_yield': info.get('dividendYield', 0),
                'eps_ttm': info.get('trailingEps', None),
                'revenue': info.get('totalRevenue', 0),
                'profit_margin': info.get('profitMargins', None),
                'roe': info.get('returnOnEquity', None),
                'debt_to_equity': info.get('debtToEquity', None),
                'current_ratio': info.get('currentRatio', None),
                'beta': info.get('beta', None),
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh', None),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow', None)
            }

            logger.info(f"Fetched company info for {symbol}")
            return company_data

        except Exception as e:
            logger.error(f"Error fetching company info for {symbol}: {e}")
            return {'symbol': symbol, 'error': str(e)}

    def get_news(self, symbol: str, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get recent news for symbol

        Args:
            symbol: Stock ticker
            days: Number of days of news to fetch

        Returns:
            List of news articles
        """
        news_articles = []

        # Try yfinance news first
        try:
            ticker = yf.Ticker(symbol)
            news = ticker.news

            for article in news[:10]:  # Limit to 10 articles
                news_articles.append({
                    'title': article.get('title', ''),
                    'publisher': article.get('publisher', ''),
                    'link': article.get('link', ''),
                    'publish_time': datetime.fromtimestamp(
                        article.get('providerPublishTime', 0)
                    ).isoformat() if article.get('providerPublishTime') else None,
                    'type': article.get('type', ''),
                    'thumbnail': article.get('thumbnail', {}).get('resolutions', [{}])[0].get('url', '')
                })

            logger.info(f"Fetched {len(news_articles)} news articles for {symbol}")

        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {e}")

        # Try Finnhub if available and no news yet
        if not news_articles and self.finnhub_key:
            try:
                news_articles = self._get_finnhub_news(symbol, days)
            except Exception as e:
                logger.error(f"Finnhub news error: {e}")

        return news_articles

    def _get_finnhub_news(self, symbol: str, days: int) -> List[Dict[str, Any]]:
        """Get news from Finnhub API"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            url = f"https://finnhub.io/api/v1/company-news"
            params = {
                'symbol': symbol,
                'from': start_date.strftime('%Y-%m-%d'),
                'to': end_date.strftime('%Y-%m-%d'),
                'token': self.finnhub_key
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                articles = response.json()
                return [{
                    'title': article.get('headline', ''),
                    'summary': article.get('summary', ''),
                    'source': article.get('source', ''),
                    'url': article.get('url', ''),
                    'publish_date': datetime.fromtimestamp(
                        article.get('datetime', 0)
                    ).isoformat() if article.get('datetime') else None
                } for article in articles[:10]]

        except Exception as e:
            logger.error(f"Finnhub API error: {e}")

        return []

    def get_market_status(self) -> Dict[str, Any]:
        """Get current market status"""
        try:
            # Get S&P 500 as market indicator
            spy = yf.Ticker("SPY")
            info = spy.info

            return {
                'market_state': info.get('marketState', 'UNKNOWN'),
                'is_open': info.get('marketState') == 'REGULAR',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting market status: {e}")
            return {'market_state': 'UNKNOWN', 'is_open': False}
