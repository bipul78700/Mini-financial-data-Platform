"""
FastAPI Routes
All API endpoints for the Stock Data Intelligence Dashboard
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime, timedelta
import pandas as pd

from models.database import get_db, StockData
from data.collector import StockDataCollector
from data.processor import StockDataProcessor
from utils.helpers import calculate_correlation, calculate_performance_metrics

router = APIRouter()

# Initialize collectors and processors
collector = StockDataCollector(period="1y")
processor = StockDataProcessor()


@router.get("/companies")
async def get_companies():
    """
    Get list of available companies
    
    Returns:
        List of company symbols
    """
    try:
        companies = collector.get_available_companies()
        return {
            "status": "success",
            "count": len(companies),
            "companies": companies
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching companies: {str(e)}")


@router.get("/data/{symbol}")
async def get_stock_data(
    symbol: str,
    days: int = Query(30, ge=1, le=365, description="Number of days of data to retrieve"),
    db: Session = Depends(get_db)
):
    """
    Get stock data for a specific symbol (last N days)
    
    Args:
        symbol: Company symbol (e.g., TCS, INFY)
        days: Number of days of data to retrieve (default: 30, max: 365)
        db: Database session
        
    Returns:
        JSON response with stock data
    """
    try:
        symbol_upper = symbol.upper()
        
        # Check if company is available
        if symbol_upper not in collector.get_available_companies():
            raise HTTPException(
                status_code=404,
                detail=f"Company '{symbol}' not found. Available companies: {collector.get_available_companies()}"
            )
        
        # Query database for recent data
        cutoff_date = datetime.now().date() - timedelta(days=days)
        db_records = db.query(StockData).filter(
            StockData.symbol == symbol_upper,
            StockData.date >= cutoff_date
        ).order_by(desc(StockData.date)).limit(days).all()
        
        # If no data in DB or insufficient data, fetch fresh data
        if len(db_records) < days:
            # Fetch fresh data
            df = collector.fetch_stock_data(symbol_upper)
            if df is None or df.empty:
                raise HTTPException(status_code=404, detail=f"No data available for {symbol}")
            
            # Process data
            df_processed = processor.process_data(df)
            
            # Store in database (async operation, but we'll do it synchronously for simplicity)
            # For production, consider background tasks
            
            # Get last N days
            df_processed = df_processed.tail(days)
        else:
            # Convert DB records to DataFrame
            data_list = []
            for record in db_records:
                data_list.append({
                    'date': record.date,
                    'open': record.open,
                    'high': record.high,
                    'low': record.low,
                    'close': record.close,
                    'volume': record.volume,
                    'daily_return': record.daily_return,
                    'ma_7': record.ma_7,
                    'volatility_score': record.volatility_score
                })
            df_processed = pd.DataFrame(data_list)
            # Sort by date (ascending) for consistent ordering
            df_processed = df_processed.sort_values('date').reset_index(drop=True)
        
        # Convert to JSON-serializable format
        df_processed['date'] = pd.to_datetime(df_processed['date']).dt.strftime('%Y-%m-%d')
        records = df_processed.to_dict('records')
        
        return {
            "status": "success",
            "symbol": symbol_upper,
            "days": len(records),
            "data": records
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")


@router.get("/summary/{symbol}")
async def get_stock_summary(
    symbol: str,
    db: Session = Depends(get_db)
):
    """
    Get summary statistics for a stock (52-week high, low, avg close)
    
    Args:
        symbol: Company symbol
        db: Database session
        
    Returns:
        Summary statistics
    """
    try:
        symbol_upper = symbol.upper()
        
        # Check if company is available
        if symbol_upper not in collector.get_available_companies():
            raise HTTPException(
                status_code=404,
                detail=f"Company '{symbol}' not found"
            )
        
        # Fetch full year of data
        df = collector.fetch_stock_data(symbol_upper, period="1y")
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail=f"No data available for {symbol}")
        
        # Process data
        df_processed = processor.process_data(df)
        
        # Get summary stats
        summary = processor.get_summary_stats(df_processed)
        
        return {
            "status": "success",
            "symbol": symbol_upper,
            "summary": summary
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching summary: {str(e)}")


@router.get("/compare")
async def compare_stocks(
    symbol1: str = Query(..., description="First stock symbol"),
    symbol2: str = Query(..., description="Second stock symbol"),
    db: Session = Depends(get_db)
):
    """
    Compare performance between two stocks
    
    Args:
        symbol1: First company symbol
        symbol2: Second company symbol
        db: Database session
        
    Returns:
        Comparison metrics
    """
    try:
        symbol1_upper = symbol1.upper()
        symbol2_upper = symbol2.upper()
        
        # Validate symbols
        available = collector.get_available_companies()
        if symbol1_upper not in available:
            raise HTTPException(status_code=404, detail=f"Company '{symbol1}' not found")
        if symbol2_upper not in available:
            raise HTTPException(status_code=404, detail=f"Company '{symbol2}' not found")
        
        # Fetch data for both stocks
        df1 = collector.fetch_stock_data(symbol1_upper, period="1y")
        df2 = collector.fetch_stock_data(symbol2_upper, period="1y")
        
        if df1 is None or df1.empty:
            raise HTTPException(status_code=404, detail=f"No data available for {symbol1}")
        if df2 is None or df2.empty:
            raise HTTPException(status_code=404, detail=f"No data available for {symbol2}")
        
        # Process both datasets
        df1_processed = processor.process_data(df1)
        df2_processed = processor.process_data(df2)
        
        # Calculate performance metrics
        metrics1 = calculate_performance_metrics(df1_processed)
        metrics2 = calculate_performance_metrics(df2_processed)
        
        # Calculate correlation
        correlation = calculate_correlation(df1_processed, df2_processed)
        
        # Get summary stats
        summary1 = processor.get_summary_stats(df1_processed)
        summary2 = processor.get_summary_stats(df2_processed)
        
        return {
            "status": "success",
            "comparison": {
                "symbol1": symbol1_upper,
                "symbol2": symbol2_upper,
                "correlation": round(correlation, 4),
                "symbol1_metrics": {
                    **metrics1,
                    "high_52w": summary1.get('high_52w', 0),
                    "low_52w": summary1.get('low_52w', 0),
                    "avg_close": summary1.get('avg_close', 0)
                },
                "symbol2_metrics": {
                    **metrics2,
                    "high_52w": summary2.get('high_52w', 0),
                    "low_52w": summary2.get('low_52w', 0),
                    "avg_close": summary2.get('avg_close', 0)
                },
                "insights": {
                    "better_performer": symbol1_upper if metrics1.get('total_return_pct', 0) > metrics2.get('total_return_pct', 0) else symbol2_upper,
                    "return_difference": round(abs(metrics1.get('total_return_pct', 0) - metrics2.get('total_return_pct', 0)), 2),
                    "correlation_interpretation": "Strong positive" if correlation > 0.7 else "Moderate positive" if correlation > 0.3 else "Weak" if correlation > -0.3 else "Negative"
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing stocks: {str(e)}")
