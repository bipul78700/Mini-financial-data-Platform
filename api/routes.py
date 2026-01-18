"""
FastAPI Routes
All API endpoints for the Stock Data Intelligence Dashboard
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from datetime import datetime, timedelta
import pandas as pd
import logging

from models.database import get_db, StockData
from data.collector import StockDataCollector
from data.processor import StockDataProcessor
from utils.helpers import calculate_correlation, calculate_performance_metrics

logger = logging.getLogger(__name__)

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
        if not companies:
            logger.warning("No companies available")
            return {
                "status": "success",
                "count": 0,
                "companies": []
            }
        return {
            "status": "success",
            "count": len(companies),
            "companies": companies
        }
    except Exception as e:
        logger.error(f"Error fetching companies: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error fetching companies: {str(e)}")


@router.get("/data/{symbol}")
async def get_stock_data(
    symbol: str,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    try:
        # Validate and normalize symbol
        if not symbol or not isinstance(symbol, str):
            raise HTTPException(status_code=400, detail="Invalid symbol parameter")
        
        symbol = symbol.upper().strip()
        if not symbol:
            raise HTTPException(status_code=400, detail="Symbol cannot be empty")

        available_companies = collector.get_available_companies()
        if symbol not in available_companies:
            raise HTTPException(
                status_code=404, 
                detail=f"Company '{symbol}' not found. Available companies: {', '.join(available_companies)}"
            )

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

        # ✅ CASE 1: DB has sufficient data
        if db_records and len(db_records) >= days:
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
            # Sort by date ascending for consistent ordering
            df = df.sort_values("date").reset_index(drop=True)

        # ✅ CASE 2: DB empty or insufficient data → FETCH + SAVE
        else:
            logger.info(f"Fetching fresh data for {symbol} (DB has {len(db_records) if db_records else 0} records)")
            df = collector.fetch_stock_data(symbol)
            if df is None or df.empty:
                raise HTTPException(status_code=404, detail="No stock data available")

            # Process data first, then limit to requested days
            df = processor.process_data(df)
            df = df.sort_values("date").reset_index(drop=True)
            df = df.tail(days) if len(df) > days else df

            # Get existing dates to avoid duplicates
            existing_dates = set()
            if db_records:
                existing_dates = {r.date for r in db_records}

            # Insert only new records
            new_records = []
            for _, row in df.iterrows():
                row_date = row["date"]
                if row_date not in existing_dates:
                    new_records.append(StockData(
                        symbol=symbol,
                        date=row_date,
                        open=float(row["open"]),
                        high=float(row["high"]),
                        low=float(row["low"]),
                        close=float(row["close"]),
                        volume=int(row["volume"]) if pd.notna(row["volume"]) else None,
                        daily_return=float(row.get("daily_return")) if pd.notna(row.get("daily_return")) else None,
                        ma_7=float(row.get("ma_7")) if pd.notna(row.get("ma_7")) else None,
                        volatility_score=float(row.get("volatility_score")) if pd.notna(row.get("volatility_score")) else None
                    ))

            if new_records:
                try:
                    db.bulk_save_objects(new_records)
                    db.commit()
                    logger.info(f"Saved {len(new_records)} new records for {symbol}")
                except IntegrityError:
                    db.rollback()
                    logger.warning(f"Duplicate records detected for {symbol}, skipping insert")
                except Exception as e:
                    db.rollback()
                    logger.error(f"Error saving data for {symbol}: {e}")
                    raise

        # Format date for JSON response (ensure it's a string)
        if 'date' in df.columns:
            df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")

        return {
            "status": "success",
            "symbol": symbol,
            "days": len(df),
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
    Get summary statistics for a stock from DB (production-safe)
    """
    try:
        symbol_upper = symbol.upper()

        # Fetch data from DB
        records = (
            db.query(StockData)
            .filter(StockData.symbol == symbol_upper)
            .order_by(StockData.date)
            .all()
        )

        if not records:
            raise HTTPException(
                status_code=404,
                detail=f"No data available for {symbol_upper}"
            )

        # Convert to DataFrame
        df = pd.DataFrame([
            {
                "date": r.date,
                "close": r.close
            }
            for r in records
        ])

        if df.empty or 'close' not in df.columns:
            raise HTTPException(
                status_code=404,
                detail=f"No valid data available for {symbol_upper}"
            )

        summary = {
            "high_52w": float(df["close"].max()),
            "low_52w": float(df["close"].min()),
            "avg_close": float(df["close"].mean()),
            "current_close": float(df["close"].iloc[-1])
        }

        return {
            "status": "success",
            "symbol": symbol_upper,
            "summary": summary
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching summary: {str(e)}"
        )



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
        
        # Try to fetch from DB first, then fetch from API if needed
        def get_stock_df(sym: str) -> pd.DataFrame:
            """Get stock data from DB or fetch from API"""
            db_data = (
                db.query(StockData)
                .filter(StockData.symbol == sym)
                .order_by(StockData.date)
                .all()
            )
            
            if db_data and len(db_data) >= 50:  # Use DB if we have sufficient data
                logger.info(f"Using DB data for {sym}")
                return pd.DataFrame([{
                    "date": r.date,
                    "open": r.open,
                    "high": r.high,
                    "low": r.low,
                    "close": r.close,
                    "volume": r.volume,
                    "daily_return": r.daily_return,
                    "ma_7": r.ma_7,
                    "volatility_score": r.volatility_score
                } for r in db_data])
            else:
                logger.info(f"Fetching fresh data for {sym}")
                df = collector.fetch_stock_data(sym, period="1y")
                if df is None or df.empty:
                    raise HTTPException(status_code=404, detail=f"No data available for {sym}")
                return processor.process_data(df)
        
        # Fetch data for both stocks
        df1_processed = get_stock_df(symbol1_upper)
        df2_processed = get_stock_df(symbol2_upper)
        
        if df1_processed is None or df1_processed.empty:
            raise HTTPException(status_code=404, detail=f"No data available for {symbol1}")
        if df2_processed is None or df2_processed.empty:
            raise HTTPException(status_code=404, detail=f"No data available for {symbol2}")
        
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