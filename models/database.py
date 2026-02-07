"""
Database Models and Setup
SQLite database for storing stock data
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Index, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging
import config

logger = logging.getLogger(__name__)

# Database file path
DATABASE_URL = config.DATABASE_URL

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
    
    # Create composite index and unique constraint to prevent duplicates
    __table_args__ = (
        Index('idx_symbol_date', 'symbol', 'date'),
        UniqueConstraint('symbol', 'date', name='uq_symbol_date'),
    )
    
    def __repr__(self):
        return f"<StockData(symbol={self.symbol}, date={self.date}, close={self.close})>"


def init_db():
    """Initialize database by creating all tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
