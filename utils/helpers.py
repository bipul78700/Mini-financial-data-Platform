"""
Utility Helper Functions
"""

from typing import List, Dict, Optional
import pandas as pd
from datetime import datetime, timedelta


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
        # Merge on date to align data
        merged = pd.merge(
            df1[['date', 'close']],
            df2[['date', 'close']],
            on='date',
            suffixes=('_1', '_2')
        )
        
        if len(merged) < 2:
            return 0.0
        
        correlation = merged['close_1'].corr(merged['close_2'])
        return float(correlation) if not pd.isna(correlation) else 0.0
    except Exception as e:
        print(f"Error calculating correlation: {e}")
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
        print(f"Error calculating performance metrics: {e}")
        return {}
