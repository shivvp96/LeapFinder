import pandas as pd
import numpy as np
from typing import Union

def format_currency(value: Union[int, float], precision: int = 1) -> str:
    """Format currency values in billions/millions/thousands"""
    if pd.isna(value) or value == 0:
        return "N/A"
    
    abs_value = abs(value)
    
    if abs_value >= 1e12:
        return f"${value/1e12:.{precision}f}T"
    elif abs_value >= 1e9:
        return f"${value/1e9:.{precision}f}B"
    elif abs_value >= 1e6:
        return f"${value/1e6:.{precision}f}M"
    elif abs_value >= 1e3:
        return f"${value/1e3:.{precision}f}K"
    else:
        return f"${value:.2f}"

def format_percentage(value: Union[int, float], precision: int = 1) -> str:
    """Format percentage values"""
    if pd.isna(value):
        return "N/A"
    return f"{value:.{precision}f}%"

def format_ratio(value: Union[int, float], precision: int = 2) -> str:
    """Format ratio values"""
    if pd.isna(value):
        return "N/A"
    return f"{value:.{precision}f}"

def get_color_for_sentiment(sentiment: str) -> str:
    """Get color code for sentiment"""
    color_map = {
        'BULLISH': '#00C851',    # Green
        'NEUTRAL': '#ffbb33',    # Orange/Yellow
        'BEARISH': '#ff4444'     # Red
    }
    return color_map.get(sentiment, '#6c757d')  # Default gray

def calculate_historical_volatility(prices: pd.Series, window: int = 30) -> float:
    """Calculate historical volatility from price series"""
    if len(prices) < window:
        return np.nan
    
    # Calculate returns
    returns = prices.pct_change().dropna()
    
    if len(returns) < window - 1:
        return np.nan
    
    # Use the most recent 'window' returns
    recent_returns = returns.tail(window)
    
    # Annualized volatility (assuming 252 trading days)
    volatility = recent_returns.std() * np.sqrt(252) * 100
    
    return volatility

def calculate_score(row: pd.DataFrame) -> float:
    """Calculate a composite score for ranking stocks"""
    try:
        # Base score from IV/HV ratio
        base_score = row['iv_hv_ratio']
        
        # Sentiment multiplier
        sentiment_multiplier = {
            'BULLISH': 1.2,
            'NEUTRAL': 1.0,
            'BEARISH': 0.8
        }.get(row['sentiment'], 1.0)
        
        # Confidence multiplier
        confidence_multiplier = 0.5 + (row['sentiment_confidence'] * 0.5)
        
        # Drop from ATH bonus (more drop = higher potential upside)
        drop_bonus = 1 + (row['drop_from_ath_pct'] / 100)
        
        # Market cap adjustment (prefer larger, more stable companies)
        market_cap_adj = min(1.1, 1 + (row['market_cap'] / 1e12))  # Max 10% bonus for $1T+ companies
        
        # Calculate final score
        final_score = (base_score * sentiment_multiplier * confidence_multiplier * 
                      drop_bonus * market_cap_adj)
        
        return round(final_score, 3)
        
    except Exception as e:
        print(f"Error calculating score: {str(e)}")
        return 0.0

def validate_dataframe(df: pd.DataFrame, required_columns: list) -> bool:
    """Validate that DataFrame has required columns"""
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"Missing required columns: {missing_columns}")
        return False
    
    return True

def clean_ticker_symbol(ticker: str) -> str:
    """Clean and validate ticker symbol"""
    if not ticker:
        return ""
    
    # Remove common suffixes and clean
    ticker = ticker.upper().strip()
    ticker = ticker.replace('.', '-')  # Yahoo Finance format
    
    # Remove any trailing characters that aren't alphanumeric or dash
    ticker = ''.join(c for c in ticker if c.isalnum() or c == '-')
    
    return ticker

def get_trading_days_between(start_date, end_date) -> int:
    """Calculate number of trading days between two dates"""
    try:
        # Simple approximation: ~252 trading days per year
        total_days = (end_date - start_date).days
        trading_days = int(total_days * (252/365))
        return max(1, trading_days)  # At least 1 day
    except:
        return 30  # Default fallback

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if division by zero"""
    try:
        if denominator == 0 or pd.isna(denominator) or pd.isna(numerator):
            return default
        return numerator / denominator
    except:
        return default
