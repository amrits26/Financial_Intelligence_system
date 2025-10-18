"""Helper Utilities for Financial Intelligence System"""
import numpy as np
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def format_currency(amount: float) -> str:
    """Format number as currency"""
    if amount is None or pd.isna(amount):
        return "N/A"
    if abs(amount) >= 1e9:
        return f"${amount/1e9:.2f}B"
    elif abs(amount) >= 1e6:
        return f"${amount/1e6:.2f}M"
    elif abs(amount) >= 1e3:
        return f"${amount/1e3:.2f}K"
    return f"${amount:.2f}"

def format_percentage(value: float, decimals: int = 2) -> str:
    """Format as percentage"""
    if value is None or pd.isna(value):
        return "N/A"
    return f"{value:.{decimals}f}%"

def calculate_returns(prices: pd.Series) -> pd.Series:
    """Calculate returns"""
    return prices.pct_change().dropna()

def calculate_volatility(returns: pd.Series, annualize: bool = True) -> float:
    """Calculate volatility"""
    vol = returns.std()
    return vol * np.sqrt(252) if annualize else vol

def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.045) -> float:
    """Calculate Sharpe ratio"""
    try:
        excess = returns - (risk_free_rate / 252)
        return (excess.mean() / excess.std()) * np.sqrt(252) if excess.std() > 0 else 0
    except:
        return np.nan

def calculate_max_drawdown(prices: pd.Series) -> float:
    """Calculate maximum drawdown"""
    try:
        cum = (1 + prices.pct_change()).cumprod()
        running_max = cum.expanding().max()
        drawdown = (cum - running_max) / running_max
        return drawdown.min()
    except:
        return np.nan

def calculate_var(returns: pd.Series, confidence: float = 0.95) -> float:
    """Calculate Value at Risk"""
    return np.percentile(returns, (1 - confidence) * 100)

def calculate_beta(stock_returns: pd.Series, market_returns: pd.Series) -> float:
    """Calculate beta"""
    try:
        aligned = pd.concat([stock_returns, market_returns], axis=1).dropna()
        if len(aligned) < 10:
            return np.nan
        cov = np.cov(aligned.iloc[:, 0], aligned.iloc[:, 1])[0][1]
        var = np.var(aligned.iloc[:, 1])
        return cov / var if var > 0 else np.nan
    except:
        return np.nan

def weighted_average(values: list, weights: list) -> float:
    """Weighted average"""
    return sum(v * w for v, w in zip(values, weights)) / sum(weights)

def detect_market_trend(prices: pd.Series, window: int = 50) -> dict:
    """Detect market trend"""
    if len(prices) < window:
        return {"trend": "Unknown", "strength": 0}

    current = prices.iloc[-1]
    ma = prices.rolling(window=window).mean().iloc[-1]

    if current > ma * 1.02:
        return {"trend": "Uptrend", "strength": ((current - ma) / ma) * 100}
    elif current < ma * 0.98:
        return {"trend": "Downtrend", "strength": ((ma - current) / ma) * 100}
    return {"trend": "Sideways", "strength": 0}
