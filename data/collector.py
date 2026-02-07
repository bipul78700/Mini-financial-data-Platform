"""
Data Collection Module
Fetches stock market data using yfinance library
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Optional
import logging

# --------------------------------------------------
# Logging setup
# --------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StockDataCollector:
    """
    Collects stock market data from yfinance API
    Supports Indian stocks (NSE/BSE) and international stocks
    """

    # Indian stock symbols mapping (NSE format)
    INDIAN_STOCKS = {
        "TCS": "TCS.NS",
        "INFY": "INFY.NS",
        "RELIANCE": "RELIANCE.NS",
        "HDFCBANK": "HDFCBANK.NS",
        "ICICIBANK": "ICICIBANK.NS",
        "WIPRO": "WIPRO.NS",
        "HCLTECH": "HCLTECH.NS",
    }

    # --------------------------------------------------
    # Constructor
    # --------------------------------------------------
    def __init__(self, period: str = "1y"):
        """
        Args:
            period: Time period (e.g. '30', '1y', '6mo')
        """
        self.period = period
        self.available_companies = list(self.INDIAN_STOCKS.keys())

    # --------------------------------------------------
    # Public helpers
    # --------------------------------------------------
    def get_available_companies(self) -> List[str]:
        """Returns list of available company symbols"""
        return self.available_companies

    # --------------------------------------------------
    # Core fetch logic
    # --------------------------------------------------
    def fetch_stock_data(
        self, symbol: str, period: Optional[str] = None
    ) -> Optional[pd.DataFrame]:
        """
        Fetch stock data for a single symbol
        """
        try:
            # Map symbol to yfinance format
            yf_symbol = self.INDIAN_STOCKS.get(symbol.upper(), symbol)

            fetch_period = period or self.period
            logger.info(
                f"Fetching data for {symbol} ({yf_symbol}) | period={fetch_period}"
            )

            ticker = yf.Ticker(yf_symbol, session=None)
            end_date = datetime.now()

            # ----------------------------------------------
            # SAFE period handling
            # ----------------------------------------------
            if fetch_period.isdigit():
                days = int(fetch_period)
                start_date = end_date - timedelta(days=days)
                df = ticker.history(start=start_date, end=end_date, timeout=15, threads=False)
            else:
                df = ticker.history(period=fetch_period, timeout=15, threads=False)

            # ----------------------------------------------
            # Fallback for cloud (Render blocks NSE)
            # ----------------------------------------------
            if df.empty and yf_symbol.endswith(".NS"):
                logger.warning(
                    f"NSE blocked for {symbol}, retrying global symbol"
                )
                ticker = yf.Ticker(symbol, session=None)
                if fetch_period.isdigit():
                    df = ticker.history(start=start_date, end=end_date)
                else:
                    df = ticker.history(period=fetch_period)

            # ----------------------------------------------
            # No data → exit
            # ----------------------------------------------
            if df.empty:
                logger.warning(f"No data found for symbol {symbol}")
                return None

            # ----------------------------------------------
            # Cleanup & formatting
            # ----------------------------------------------
            df.reset_index(inplace=True)
            df.columns = [c.lower().replace(" ", "_") for c in df.columns]

            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"]).dt.date

            logger.info(
                f"Successfully fetched {len(df)} records for {symbol}"
            )
            return df

        except Exception as e:
            logger.exception(f"Error fetching data for {symbol}")
            return None

    # --------------------------------------------------
    # Fetch multiple stocks
    # --------------------------------------------------
    def fetch_multiple_stocks(
        self, symbols: List[str], period: Optional[str] = None
    ) -> dict:
        """
        Fetch data for multiple stocks
        """
        data_dict = {}

        for symbol in symbols:
            df = self.fetch_stock_data(symbol, period)
            if df is not None:
                data_dict[symbol] = df

        return data_dict
