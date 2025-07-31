"""Database models for Screening Bot V2."""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List

from sqlalchemy import (
    Boolean,
    Column, 
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped, mapped_column

Base = declarative_base()


class Cryptocurrency(Base):
    """Model for cryptocurrency basic information."""
    
    __tablename__ = 'cryptocurrencies'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    coin_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    market_cap_rank: Mapped[Optional[int]] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    historical_prices: Mapped[List["HistoricalPrice"]] = relationship("HistoricalPrice", back_populates="cryptocurrency")
    sma_indicators: Mapped[List["SMAIndicator"]] = relationship("SMAIndicator", back_populates="cryptocurrency")
    screening_results: Mapped[List["ScreeningResult"]] = relationship("ScreeningResult", back_populates="cryptocurrency")
    
    def __repr__(self):
        return f"<Cryptocurrency(coin_id='{self.coin_id}', name='{self.name}', symbol='{self.symbol}')>"


class HistoricalPrice(Base):
    """Model for historical price data."""
    
    __tablename__ = 'historical_prices'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cryptocurrency_id: Mapped[int] = mapped_column(Integer, ForeignKey('cryptocurrencies.id'), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    price_usd: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 10))
    price_btc: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 10))
    volume_usd: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 2))
    market_cap_usd: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 2))
    high_24h: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 10))
    low_24h: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 10))
    price_change_24h_pct: Mapped[Optional[float]] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    cryptocurrency: Mapped["Cryptocurrency"] = relationship("Cryptocurrency", back_populates="historical_prices")
    
    __table_args__ = (
        UniqueConstraint('cryptocurrency_id', 'date', name='uq_crypto_date'),
        Index('ix_historical_prices_date', 'date'),
        Index('ix_historical_prices_crypto_date', 'cryptocurrency_id', 'date')
    )
    
    def __repr__(self):
        return f"<HistoricalPrice(crypto_id={self.cryptocurrency_id}, date='{self.date}', price_btc={self.price_btc})>"


class SMAIndicator(Base):
    """Model for Simple Moving Average indicators."""
    
    __tablename__ = 'sma_indicators'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cryptocurrency_id: Mapped[int] = mapped_column(Integer, ForeignKey('cryptocurrencies.id'), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    sma_6: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 10))
    sma_11: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 10))
    sma_21: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 10))
    above_sma_6: Mapped[Optional[int]] = mapped_column(Integer)  # 1 or -1
    above_sma_11: Mapped[Optional[int]] = mapped_column(Integer)  # 2 or -2
    above_sma_21: Mapped[Optional[int]] = mapped_column(Integer)  # 3 or -3
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    cryptocurrency: Mapped["Cryptocurrency"] = relationship("Cryptocurrency", back_populates="sma_indicators")
    
    __table_args__ = (
        UniqueConstraint('cryptocurrency_id', 'date', name='uq_sma_crypto_date'),
        Index('ix_sma_indicators_date', 'date'),
        Index('ix_sma_indicators_crypto_date', 'cryptocurrency_id', 'date')
    )
    
    def __repr__(self):
        return f"<SMAIndicator(crypto_id={self.cryptocurrency_id}, date='{self.date}')>"


class ScreeningResult(Base):
    """Model for screening analysis results."""
    
    __tablename__ = 'screening_results'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cryptocurrency_id: Mapped[int] = mapped_column(Integer, ForeignKey('cryptocurrencies.id'), nullable=False)
    analysis_date: Mapped[date] = mapped_column(Date, nullable=False)
    timeframe_days: Mapped[int] = mapped_column(Integer, nullable=False)  # e.g., 1, 2, 3, etc.
    direction: Mapped[str] = mapped_column(String(20), nullable=False)  # 'forward' or 'backward'
    
    # Performance metrics
    cumulative_return: Mapped[Optional[float]] = mapped_column(Float)
    rank_position: Mapped[Optional[int]] = mapped_column(Integer)
    rank_change: Mapped[Optional[float]] = mapped_column(Float)
    
    # Scoring components
    day_rank_score: Mapped[Optional[int]] = mapped_column(Integer)
    sma_fast_score: Mapped[Optional[int]] = mapped_column(Integer)
    sma_medium_score: Mapped[Optional[int]] = mapped_column(Integer)
    sma_slow_score: Mapped[Optional[int]] = mapped_column(Integer)
    top_10_score: Mapped[Optional[int]] = mapped_column(Integer)
    change_type_score: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Final scores
    total_score: Mapped[Optional[float]] = mapped_column(Float)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    analysis_parameters: Mapped[Optional[str]] = mapped_column(Text)  # JSON string with analysis config
    
    # Relationships
    cryptocurrency: Mapped["Cryptocurrency"] = relationship("Cryptocurrency", back_populates="screening_results")
    
    __table_args__ = (
        UniqueConstraint('cryptocurrency_id', 'analysis_date', 'timeframe_days', 'direction', 
                        name='uq_screening_result'),
        Index('ix_screening_results_analysis_date', 'analysis_date'),
        Index('ix_screening_results_score', 'total_score'),
        Index('ix_screening_results_crypto_timeframe', 'cryptocurrency_id', 'timeframe_days', 'direction')
    )
    
    def __repr__(self):
        return f"<ScreeningResult(crypto_id={self.cryptocurrency_id}, date='{self.analysis_date}', score={self.total_score})>"


class CacheEntry(Base):
    """Model for caching API responses and computed results."""
    
    __tablename__ = 'cache_entries'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cache_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    cache_value: Mapped[str] = mapped_column(Text, nullable=False)  # JSON string
    cache_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'api_response', 'computed_result', etc.
    ttl_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    @property
    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        return datetime.utcnow() > self.expires_at
    
    def __repr__(self):
        return f"<CacheEntry(key='{self.cache_key}', expires_at='{self.expires_at}')>"