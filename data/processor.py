"""
Data Processing Module
Cleans and processes stock market data, calculates metrics
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StockDataProcessor:
    """
    Processes and enriches stock market data with calculated metrics
    """
    
    def __init__(self):
        """Initialize the data processor"""
        pass
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cleans stock data by handling missing values and invalid data
        
        Args:
            df: Raw stock data DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        if df is None or df.empty:
            return df
        
        df_clean = df.copy()
        
        # Remove rows with all NaN values
        df_clean = df_clean.dropna(how='all')
        
        # Forward fill missing values for price columns (carry last known value)
        price_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in price_columns:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].ffill()
        
        # Backward fill any remaining NaN values
        df_clean = df_clean.bfill()
        
        # Remove rows where close price is 0 or negative (invalid data)
        if 'close' in df_clean.columns:
            df_clean = df_clean[df_clean['close'] > 0]
        
        # Ensure date column is properly formatted
        if 'date' in df_clean.columns:
            df_clean['date'] = pd.to_datetime(df_clean['date']).dt.date
        
        # Sort by date
        if 'date' in df_clean.columns:
            df_clean = df_clean.sort_values('date').reset_index(drop=True)
        
        logger.info(f"Cleaned data: {len(df_clean)} records remaining")
        return df_clean
    
    def calculate_daily_return(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates daily return: (Close - Open) / Open
        
        Args:
            df: Stock data DataFrame
            
        Returns:
            DataFrame with daily_return column added
        """
        df_result = df.copy()
        
        if 'open' in df_result.columns and 'close' in df_result.columns:
            df_result['daily_return'] = (df_result['close'] - df_result['open']) / df_result['open']
            df_result['daily_return'] = df_result['daily_return'].fillna(0)
        else:
            logger.warning("Missing 'open' or 'close' columns for daily return calculation")
        
        return df_result
    
    def calculate_moving_average(self, df: pd.DataFrame, window: int = 7) -> pd.DataFrame:
        """
        Calculates moving average for specified window
        
        Args:
            df: Stock data DataFrame
            window: Number of days for moving average (default: 7)
            
        Returns:
            DataFrame with moving_average column added
        """
        df_result = df.copy()
        
        if 'close' in df_result.columns:
            df_result[f'ma_{window}'] = df_result['close'].rolling(window=window, min_periods=1).mean()
        else:
            logger.warning("Missing 'close' column for moving average calculation")
        
        return df_result
    
    def calculate_52week_high_low(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculates 52-week high and low prices
        
        Args:
            df: Stock data DataFrame (should contain at least 1 year of data)
            
        Returns:
            Dictionary with 'high_52w' and 'low_52w' values
        """
        result = {}
        
        if 'high' in df.columns and 'low' in df.columns:
            # Get last 52 weeks (or all available data if less)
            df_52w = df.tail(252) if len(df) >= 252 else df  # ~252 trading days in a year
            
            result['high_52w'] = float(df_52w['high'].max())
            result['low_52w'] = float(df_52w['low'].min())
        else:
            logger.warning("Missing 'high' or 'low' columns for 52-week calculation")
            result['high_52w'] = 0.0
            result['low_52w'] = 0.0
        
        return result
    
    def calculate_volatility_score(self, df: pd.DataFrame, window: int = 30) -> pd.DataFrame:
        """
        Calculates volatility score (creative metric)
        Volatility Score = Standard Deviation of Daily Returns over rolling window
        
        Args:
            df: Stock data DataFrame
            window: Rolling window for volatility calculation (default: 30 days)
            
        Returns:
            DataFrame with volatility_score column added
        """
        df_result = df.copy()
        
        # First ensure daily_return is calculated
        if 'daily_return' not in df_result.columns:
            df_result = self.calculate_daily_return(df_result)
        
        if 'daily_return' in df_result.columns:
            # Calculate rolling standard deviation of daily returns
            df_result['volatility_score'] = df_result['daily_return'].rolling(
                window=window, min_periods=1
            ).std() * np.sqrt(252)  # Annualized volatility
            
            df_result['volatility_score'] = df_result['volatility_score'].fillna(0)
        else:
            logger.warning("Could not calculate volatility score")
        
        return df_result
    
    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Complete data processing pipeline
        
        Args:
            df: Raw stock data DataFrame
            
        Returns:
            Fully processed DataFrame with all metrics
        """
        if df is None or df.empty:
            return df
        
        logger.info("Starting data processing pipeline")
        
        # Step 1: Clean data
        df_processed = self.clean_data(df)
        
        # Step 2: Calculate daily return
        df_processed = self.calculate_daily_return(df_processed)
        
        # Step 3: Calculate 7-day moving average
        df_processed = self.calculate_moving_average(df_processed, window=7)
        
        # Step 4: Calculate volatility score (creative metric)
        df_processed = self.calculate_volatility_score(df_processed, window=30)
        
        logger.info("Data processing pipeline completed")
        return df_processed
    
    def get_summary_stats(self, df: pd.DataFrame) -> Dict:
        """
        Calculates summary statistics for a stock
        
        Args:
            df: Processed stock data DataFrame
            
        Returns:
            Dictionary with summary statistics
        """
        if df is None or df.empty:
            return {}
        
        # Get 52-week high/low
        week52_stats = self.calculate_52week_high_low(df)
        
        # Calculate average close price
        avg_close = float(df['close'].mean()) if 'close' in df.columns else 0.0
        
        # Get latest values safely
        latest = None
        current_close = 0.0
        if len(df) > 0:
            try:
                latest = df.iloc[-1]
                if latest is not None and 'close' in latest and pd.notna(latest['close']):
                    current_close = float(latest['close'])
            except (IndexError, KeyError) as e:
                logger.warning(f"Error getting latest close price: {e}")
        
        # Get date range safely
        date_start = None
        date_end = None
        if 'date' in df.columns and len(df) > 0:
            try:
                date_start = str(df['date'].min())
                date_end = str(df['date'].max())
            except Exception as e:
                logger.warning(f"Error getting date range: {e}")
        
        summary = {
            'high_52w': week52_stats['high_52w'],
            'low_52w': week52_stats['low_52w'],
            'avg_close': avg_close,
            'current_close': current_close,
            'total_records': len(df),
            'date_range': {
                'start': date_start,
                'end': date_end
            }
        }
        
        return summary
