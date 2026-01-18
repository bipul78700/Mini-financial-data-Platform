"""
Utility Helper Functions
"""

from typing import List, Dict, Optional
import pandas as pd
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def format_date(date_str: str) -> Optional[datetime]:
    """
    Converts date string to datetime object
    
    Args:
        date_str: Date string in various formats
        
    Returns:
        datetime object or None
    """
    try:
        if isinstance(date_str, str):
            return pd.to_datetime(date_str).to_pydatetime()
        return date_str
    except:
        return None


def calculate_correlation(df1: pd.DataFrame, df2: pd.DataFrame) -> float:
    """
    Calculates correlation between two stocks' closing prices
    
    Args:
        df1: First stock DataFrame
        df2: Second stock DataFrame
        
    Returns:
        Correlation coefficient (float between -1 and 1)
    """
    try:
        if df1 is None or df2 is None or df1.empty or df2.empty:
            logger.warning("Empty DataFrames provided for correlation calculation")
            return 0.0
        
        if 'date' not in df1.columns or 'close' not in df1.columns:
            logger.warning("df1 missing required columns (date, close)")
            return 0.0
        
        if 'date' not in df2.columns or 'close' not in df2.columns:
            logger.warning("df2 missing required columns (date, close)")
            return 0.0
        
        # Merge on date to align data
        merged = pd.merge(
            df1[['date', 'close']],
            df2[['date', 'close']],
            on='date',
            suffixes=('_1', '_2'),
            how='inner'
        )
        
        if len(merged) < 2:
            logger.warning(f"Insufficient overlapping data points: {len(merged)}")
            return 0.0
        
        # Remove any NaN values
        merged = merged.dropna(subset=['close_1', 'close_2'])
        
        if len(merged) < 2:
            logger.warning("Insufficient valid data after removing NaN values")
            return 0.0
        
        correlation = merged['close_1'].corr(merged['close_2'])
        result = float(correlation) if not pd.isna(correlation) else 0.0
        
        # Ensure result is within valid range
        return max(-1.0, min(1.0, result))
    except Exception as e:
        logger.error(f"Error calculating correlation: {e}", exc_info=True)
        return 0.0


def calculate_performance_metrics(df: pd.DataFrame) -> Dict:
    """
    Calculates performance metrics for comparison
    
    Args:
        df: Stock data DataFrame
        
    Returns:
        Dictionary with performance metrics
    """
    if df is None or df.empty:
        return {}
    
    try:
        # Calculate total return
        if len(df) > 0:
            first_close = df.iloc[0]['close']
            last_close = df.iloc[-1]['close']
            total_return = ((last_close - first_close) / first_close) * 100 if first_close > 0 else 0.0
        else:
            total_return = 0.0
        
        # Calculate average daily return
        avg_daily_return = float(df['daily_return'].mean()) if 'daily_return' in df.columns else 0.0
        
        # Calculate volatility
        volatility = float(df['daily_return'].std()) if 'daily_return' in df.columns else 0.0
        
        return {
            'total_return_pct': round(total_return, 2),
            'avg_daily_return': round(avg_daily_return, 4),
            'volatility': round(volatility, 4),
            'max_price': float(df['close'].max()) if 'close' in df.columns else 0.0,
            'min_price': float(df['close'].min()) if 'close' in df.columns else 0.0,
            'avg_price': float(df['close'].mean()) if 'close' in df.columns else 0.0
        }
    except Exception as e:
        logger.error(f"Error calculating performance metrics: {e}")
        return {}
