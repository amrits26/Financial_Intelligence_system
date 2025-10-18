"""
Database Manager for Financial Intelligence System
Handles SQLite database operations for storing analysis results
"""
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
import pandas as pd

logger = logging.getLogger(__name__)

class Database:
    """Database manager for financial data storage"""

    def __init__(self, db_path: str = "financial_data.db"):
        self.db_path = db_path
        self.conn = None
    
    def initialize(self):
        """Initialize database with required tables"""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._create_tables()
            logger.info(f"Database initialized: {self.db_path}")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    def _create_tables(self):
        """Create database tables"""
        cursor = self.conn.cursor()
        
        # Analysis results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                analysis_type TEXT,
                results TEXT,
                confidence REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Portfolio holdings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT UNIQUE NOT NULL,
                quantity REAL,
                avg_cost REAL,
                current_price REAL,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Market data cache table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_data_cache (
                symbol TEXT PRIMARY KEY,
                data TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
        logger.info("Database tables created")
    
    def save_analysis(self, symbol: str, results: Dict[str, Any]):
        """Save analysis results"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO analyses (symbol, analysis_type, results, confidence)
                VALUES (?, ?, ?, ?)
            ''', (
                symbol,
                results.get('analysis_type', 'comprehensive'),
                json.dumps(results),
                results.get('confidence', 0.0)
            ))
            self.conn.commit()
            logger.info(f"Saved analysis for {symbol}")
        except Exception as e:
            logger.error(f"Failed to save analysis: {e}")
    
    def get_recent_analyses(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent analyses"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT symbol, analysis_type, confidence, timestamp
                FROM analyses
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'symbol': row[0],
                    'type': row[1],
                    'confidence': row[2],
                    'timestamp': row[3]
                })
            return results
        except Exception as e:
            logger.error(f"Failed to get recent analyses: {e}")
            return []
    
    def get_portfolio_holdings(self) -> Dict[str, Dict[str, Any]]:
        """Get current portfolio holdings"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT symbol, quantity, avg_cost, current_price FROM portfolio')
            
            holdings = {}
            for row in cursor.fetchall():
                holdings[row[0]] = {
                    'quantity': row[1],
                    'avg_cost': row[2],
                    'current_price': row[3],
                    'market_value': row[1] * row[3] if row[3] else 0
                }
            return holdings
        except Exception as e:
            logger.error(f"Failed to get portfolio: {e}")
            return {}
    
    def update_portfolio(self, symbol: str, quantity: float, avg_cost: float):
        """Update portfolio holding"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO portfolio (symbol, quantity, avg_cost)
                VALUES (?, ?, ?)
            ''', (symbol, quantity, avg_cost))
            self.conn.commit()
            logger.info(f"Updated portfolio: {symbol}")
        except Exception as e:
            logger.error(f"Failed to update portfolio: {e}")
    
    def cache_market_data(self, symbol: str, data: pd.DataFrame):
        """Cache market data"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO market_data_cache (symbol, data, timestamp)
                VALUES (?, ?, ?)
            ''', (symbol, data.to_json(), datetime.now()))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to cache market data: {e}")
    
    def get_cached_market_data(self, symbol: str, max_age_minutes: int = 30) -> Optional[pd.DataFrame]:
        """Get cached market data if fresh"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT data, timestamp FROM market_data_cache
                WHERE symbol = ?
                AND datetime(timestamp) > datetime('now', '-' || ? || ' minutes')
            ''', (symbol, max_age_minutes))
            
            row = cursor.fetchone()
            if row:
                return pd.read_json(row[0])
            return None
        except Exception as e:
            logger.error(f"Failed to get cached data: {e}")
            return None
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    def delete_portfolio_holding(self, symbol: str):
        """Delete portfolio holding"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM portfolio WHERE symbol = ?', (symbol,))
            self.conn.commit()
            logger.info(f"Deleted portfolio holding: {symbol}")
        except Exception as e:
            logger.error(f"Failed to delete holding: {e}")
