"""
Data Collection Module
Fetches stock market data using yfinance library
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StockDataCollector:
    """
    Collects stock market data from yfinance API
    Supports Indian stocks (NSE/BSE) and international stocks
    """
    
    # Indian stock symbols mapping (NSE format)
    INDIAN_STOCKS = {
        'TCS': 'TCS.NS',      # TCS on NSE
        'INFY': 'INFY.NS',    # Infosys on NSE
        'RELIANCE': 'RELIANCE.NS',  # Reliance on NSE
        'HDFCBANK': 'HDFCBANK.NS',
        'ICICIBANK': 'ICICIBANK.NS',
        'WIPRO': 'WIPRO.NS',
        'HCLTECH': 'HCLTECH.NS',
    }
    
    def __init__(self, period: str = "1y"):
        """
        Initialize the data collector
        
        Args:
            period: Time period for data collection (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        """
        self.period = period
        self.available_companies = list(self.INDIAN_STOCKS.keys())
    
    def get_available_companies(self) -> List[str]:
        """Returns list of available company symbols"""
        return self.available_companies
    
    def fetch_stock_data(self, symbol: str, period: Optional[str] = None) -> Optional[pd.DataFrame]:
        """
        Fetches stock data for a given symbol
        
        Args:
            symbol: Company symbol (e.g., 'TCS', 'INFY')
            period: Optional override for data period
            
        Returns:
            DataFrame with stock data or None if error
        """
        try:
            # Map Indian stock symbol to yfinance format
            yf_symbol = self.INDIAN_STOCKS.get(symbol.upper(), symbol)
            
            # Use provided period or default
            fetch_period = period or self.period
            
            logger.info(f"Fetching data for {symbol} ({yf_symbol}) for period {fetch_period}")
            
            # Fetch data from yfinance
            ticker = yf.Ticker(yf_symbol)
            df = ticker.history(period=fetch_period)
            
            if df.empty:
                logger.warning(f"No data found for symbol {symbol}")
                return None
            
            # Reset index to make Date a column
            df.reset_index(inplace=True)
            
            # Rename columns to lowercase for consistency
            df.columns = [col.lower().replace(' ', '_') for col in df.columns]
            
            # Ensure date column is properly formatted
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date']).dt.date
            
            logger.info(f"Successfully fetched {len(df)} records for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def fetch_multiple_stocks(self, symbols: List[str], period: Optional[str] = None) -> dict:
        """
        Fetches data for multiple stocks
        
        Args:
            symbols: List of company symbols
            period: Optional override for data period
            
        Returns:
            Dictionary mapping symbols to their DataFrames
        """
        data_dict = {}
        for symbol in symbols:
            df = self.fetch_stock_data(symbol, period)
            if df is not None:
                data_dict[symbol] = df
        return data_dict
