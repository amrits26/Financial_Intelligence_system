"""
Input Validation for Financial Intelligence System
Validates user inputs, stock symbols, dates, and configuration
"""
import re
from datetime import datetime, date
from typing import Union, Dict, Any

class ValidationError(Exception):
    """Custom validation error"""
    pass

def validate_stock_symbol(symbol: str) -> str:
    """
    Validate and clean stock symbol

    Args:
        symbol: Stock symbol to validate

    Returns:
        str: Cleaned symbol

    Raises:
        ValidationError: If symbol is invalid
    """
    if not symbol:
        raise ValidationError("Stock symbol cannot be empty")

    symbol = str(symbol).upper().strip()

    # Basic validation (1-5 characters, letters only, with some exceptions)
    if not re.match(r'^[A-Z]{1,5}$', symbol):
        # Allow some special cases (indices, international)
        if not (symbol.startswith('^') or '.TO' in symbol or '=' in symbol):
            raise ValidationError(f"Invalid stock symbol: {symbol}")

    return symbol

def validate_period(period: str) -> str:
    """
    Validate time period string

    Args:
        period: Period string (e.g., '1y', '6mo', '1d')

    Returns:
        str: Validated period

    Raises:
        ValidationError: If period is invalid
    """
    valid_periods = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']

    if period not in valid_periods:
        raise ValidationError(f"Invalid period: {period}. Must be one of {valid_periods}")

    return period

def validate_date_range(start_date: Union[str, date], end_date: Union[str, date]) -> tuple:
    """
    Validate date range

    Args:
        start_date: Start date
        end_date: End date

    Returns:
        tuple: (start_date, end_date) as date objects

    Raises:
        ValidationError: If dates are invalid
    """
    try:
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        if start_date >= end_date:
            raise ValidationError("Start date must be before end date")

        if start_date > datetime.now().date():
            raise ValidationError("Start date cannot be in the future")

        return start_date, end_date

    except ValueError as e:
        raise ValidationError(f"Invalid date format: {str(e)}")

def validate_portfolio_weights(weights: Dict[str, float]) -> Dict[str, float]:
    """
    Validate portfolio weights

    Args:
        weights: Dictionary of symbol -> weight

    Returns:
        Dict[str, float]: Validated weights

    Raises:
        ValidationError: If weights are invalid
    """
    if not weights:
        raise ValidationError("Portfolio weights cannot be empty")

    validated = {}
    total_weight = 0

    for symbol, weight in weights.items():
        # Validate symbol
        symbol = validate_stock_symbol(symbol)

        # Validate weight
        if not isinstance(weight, (int, float)):
            raise ValidationError(f"Weight for {symbol} must be numeric")

        if weight < 0:
            raise ValidationError(f"Weight for {symbol} cannot be negative")

        if weight > 1:
            raise ValidationError(f"Weight for {symbol} cannot exceed 1.0 (100%)")

        validated[symbol] = float(weight)
        total_weight += weight

    # Check if weights sum to approximately 1
    if abs(total_weight - 1.0) > 0.01:
        raise ValidationError(f"Portfolio weights sum to {total_weight:.3f}, must sum to 1.0")

    return validated

def validate_numerical_input(
    value: Any, 
    min_value: float = None, 
    max_value: float = None, 
    allow_none: bool = False
) -> float:
    """
    Validate numerical input with optional bounds

    Args:
        value: Value to validate
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        allow_none: Whether to allow None values

    Returns:
        float: Validated value

    Raises:
        ValidationError: If value is invalid
    """
    if value is None:
        if allow_none:
            return None
        raise ValidationError("Value cannot be None")

    try:
        num_value = float(value)
    except (TypeError, ValueError):
        raise ValidationError(f"Value must be numeric, got {type(value)}")

    if min_value is not None and num_value < min_value:
        raise ValidationError(f"Value {num_value} must be >= {min_value}")

    if max_value is not None and num_value > max_value:
        raise ValidationError(f"Value {num_value} must be <= {max_value}")

    return num_value

def sanitize_input(input_str: str, max_length: int = 1000) -> str:
    """
    Sanitize user input to prevent injection attacks

    Args:
        input_str: Input string to sanitize
        max_length: Maximum allowed length

    Returns:
        str: Sanitized string
    """
    if not isinstance(input_str, str):
        input_str = str(input_str)

    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', ';', '|', '`', '$', '\\n', '\\r']
    for char in dangerous_chars:
        input_str = input_str.replace(char, '')

    # Limit length
    input_str = input_str[:max_length]

    # Remove extra whitespace
    input_str = ' '.join(input_str.split())

    return input_str.strip()
