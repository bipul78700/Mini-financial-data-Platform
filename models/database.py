"""
Database Models and Setup
SQLite database for storing stock data
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database file path
DATABASE_URL = "sqlite:///./stock_data.db"

# Create engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


class StockData(Base):
    """
    Stock data model for storing historical stock prices
    """
    __tablename__ = "stock_data"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    date = Column(Date, nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Integer, nullable=True)
    daily_return = Column(Float, nullable=True)
    ma_7 = Column(Float, nullable=True)
    volatility_score = Column(Float, nullable=True)
    
    # Create composite index for faster queries
    __table_args__ = (
        Index('idx_symbol_date', 'symbol', 'date'),
    )
    
    def __repr__(self):
        return f"<StockData(symbol={self.symbol}, date={self.date}, close={self.close})>"


def init_db():
    """Initialize database by creating all tables"""
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully")


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
