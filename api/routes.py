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
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    try:
        symbol = symbol.upper()

        if symbol not in collector.get_available_companies():
            raise HTTPException(status_code=404, detail="Company not found")

        cutoff_date = datetime.now().date() - timedelta(days=days)

        db_records = (
            db.query(StockData)
            .filter(
                StockData.symbol == symbol,
                StockData.date >= cutoff_date
            )
            .order_by(desc(StockData.date))
            .all()
        )

        # ✅ CASE 1: DB has data
        if db_records:
            df = pd.DataFrame([{
                "date": r.date,
                "open": r.open,
                "high": r.high,
                "low": r.low,
                "close": r.close,
                "volume": r.volume,
                "daily_return": r.daily_return,
                "ma_7": r.ma_7,
                "volatility_score": r.volatility_score
            } for r in db_records])

        # ✅ CASE 2: DB empty → FETCH + SAVE
        else:
            df = collector.fetch_stock_data(symbol)
            if df is None or df.empty:
                raise HTTPException(status_code=404, detail="No stock data available")

            df = processor.process_data(df).tail(days)

            for _, row in df.iterrows():
                db.add(StockData(
                    symbol=symbol,
                    date=row["date"],
                    open=row["open"],
                    high=row["high"],
                    low=row["low"],
                    close=row["close"],
                    volume=row["volume"],
                    daily_return=row.get("daily_return"),
                    ma_7=row.get("ma_7"),
                    volatility_score=row.get("volatility_score")
                ))

            db.commit()

        df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")

        return {
            "status": "success",
            "symbol": symbol,
            "data": df.to_dict("records")
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



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