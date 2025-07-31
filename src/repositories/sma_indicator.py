"""Repository for SMA indicator operations."""

from datetime import date, timedelta
from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, desc, asc
from loguru import logger
import pandas as pd

from .base import BaseRepository
from ..database.models import SMAIndicator, Cryptocurrency


class SMAIndicatorRepository(BaseRepository[SMAIndicator]):
    """Repository for SMA indicator operations."""
    
    def __init__(self, session: Session):
        super().__init__(session, SMAIndicator)
    
    def get_by_crypto_and_date(self, cryptocurrency_id: int, date: date) -> Optional[SMAIndicator]:
        """Get SMA indicators for specific crypto and date."""
        try:
            return self.session.query(SMAIndicator).filter(
                and_(
                    SMAIndicator.cryptocurrency_id == cryptocurrency_id,
                    SMAIndicator.date == date
                )
            ).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting SMA indicators for crypto {cryptocurrency_id} on {date}: {e}")
            raise
    
    def get_sma_range(self, cryptocurrency_id: int, start_date: date, end_date: date) -> List[SMAIndicator]:
        """Get SMA indicators for a crypto within date range."""
        try:
            return self.session.query(SMAIndicator).filter(
                and_(
                    SMAIndicator.cryptocurrency_id == cryptocurrency_id,
                    SMAIndicator.date >= start_date,
                    SMAIndicator.date <= end_date
                )
            ).order_by(SMAIndicator.date.asc()).all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting SMA range for crypto {cryptocurrency_id}: {e}")
            raise
    
    def get_sma_for_date(self, target_date: date) -> List[SMAIndicator]:
        """Get all crypto SMA indicators for a specific date."""
        try:
            return self.session.query(SMAIndicator).filter(
                SMAIndicator.date == target_date
            ).options(joinedload(SMAIndicator.cryptocurrency)).all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting SMA indicators for date {target_date}: {e}")
            raise
    
    def get_above_sma_signals(self, coin_ids: List[str], days: int = 30) -> pd.DataFrame:
        """Get 'above SMA' signals as DataFrame for analysis."""
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            query = self.session.query(
                Cryptocurrency.coin_id,
                SMAIndicator.date,
                SMAIndicator.above_sma_6,
                SMAIndicator.above_sma_11,
                SMAIndicator.above_sma_21
            ).join(
                Cryptocurrency,
                SMAIndicator.cryptocurrency_id == Cryptocurrency.id
            ).filter(
                and_(
                    Cryptocurrency.coin_id.in_(coin_ids),
                    SMAIndicator.date >= start_date,
                    SMAIndicator.date <= end_date
                )
            ).order_by(SMAIndicator.date.asc())
            
            df = pd.read_sql(query.statement, self.session.bind)
            df['date'] = pd.to_datetime(df['date'])
            
            return df
        except Exception as e:
            logger.error(f"Error getting above SMA signals: {e}")
            raise
    
    def get_sma_dataframe(self, coin_ids: List[str], days: int = 30, 
                         sma_period: str = 'sma_6') -> pd.DataFrame:
        """Get SMA values as pandas DataFrame."""
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            query = self.session.query(
                Cryptocurrency.coin_id,
                SMAIndicator.date,
                getattr(SMAIndicator, sma_period)
            ).join(
                Cryptocurrency,
                SMAIndicator.cryptocurrency_id == Cryptocurrency.id
            ).filter(
                and_(
                    Cryptocurrency.coin_id.in_(coin_ids),
                    SMAIndicator.date >= start_date,
                    SMAIndicator.date <= end_date
                )
            ).order_by(SMAIndicator.date.asc())
            
            df = pd.read_sql(query.statement, self.session.bind)
            
            # Pivot to have coins as columns and dates as index
            df_pivot = df.pivot(index='date', columns='coin_id', values=sma_period)
            df_pivot.index = pd.to_datetime(df_pivot.index)
            
            return df_pivot
        except Exception as e:
            logger.error(f"Error creating SMA dataframe: {e}")
            raise
    
    def get_above_sma_dataframe(self, coin_ids: List[str], days: int = 30, 
                               sma_signal: str = 'above_sma_6') -> pd.DataFrame:
        """Get 'above SMA' signals as pandas DataFrame."""
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            query = self.session.query(
                Cryptocurrency.coin_id,
                SMAIndicator.date,
                getattr(SMAIndicator, sma_signal)
            ).join(
                Cryptocurrency,
                SMAIndicator.cryptocurrency_id == Cryptocurrency.id
            ).filter(
                and_(
                    Cryptocurrency.coin_id.in_(coin_ids),
                    SMAIndicator.date >= start_date,
                    SMAIndicator.date <= end_date
                )
            ).order_by(SMAIndicator.date.asc())
            
            df = pd.read_sql(query.statement, self.session.bind)
            
            # Pivot to have coins as columns and dates as index  
            df_pivot = df.pivot(index='date', columns='coin_id', values=sma_signal)
            df_pivot.index = pd.to_datetime(df_pivot.index)
            
            return df_pivot
        except Exception as e:
            logger.error(f"Error creating above SMA dataframe: {e}")
            raise
    
    def create_or_update_sma(self, cryptocurrency_id: int, date: date, **sma_data) -> SMAIndicator:
        """Create new SMA record or update existing one."""
        try:
            sma = self.get_by_crypto_and_date(cryptocurrency_id, date)
            
            if sma:
                # Update existing
                for key, value in sma_data.items():
                    if hasattr(sma, key):
                        setattr(sma, key, value)
                logger.debug(f"Updated SMA for crypto {cryptocurrency_id} on {date}")
            else:
                # Create new
                sma = self.create(
                    cryptocurrency_id=cryptocurrency_id,
                    date=date,
                    **sma_data
                )
                logger.debug(f"Created new SMA for crypto {cryptocurrency_id} on {date}")
            
            self.session.flush()
            return sma
        except SQLAlchemyError as e:
            logger.error(f"Error creating/updating SMA for crypto {cryptocurrency_id}: {e}")
            raise
    
    def bulk_upsert_sma(self, sma_records: List[Dict[str, Any]]) -> int:
        """Efficiently insert or update multiple SMA records."""
        try:
            updated_count = 0
            
            for record in sma_records:
                crypto_id = record['cryptocurrency_id']
                record_date = record['date']
                
                existing = self.get_by_crypto_and_date(crypto_id, record_date)
                
                if existing:
                    # Update existing record
                    for key, value in record.items():
                        if key not in ['cryptocurrency_id', 'date'] and hasattr(existing, key):
                            setattr(existing, key, value)
                else:
                    # Create new record
                    new_sma = SMAIndicator(**record)
                    self.session.add(new_sma)
                
                updated_count += 1
            
            self.session.flush()
            logger.debug(f"Bulk upserted {updated_count} SMA records")
            return updated_count
        except SQLAlchemyError as e:
            logger.error(f"Error in bulk upsert SMA: {e}")
            raise
    
    def calculate_sma_signals(self, cryptocurrency_id: int, current_price: float, 
                            sma_6: float, sma_11: float, sma_21: float) -> Dict[str, int]:
        """Calculate above SMA signals based on current price and SMA values."""
        try:
            signals = {}
            
            # Above SMA signals: positive for above, negative for below
            signals['above_sma_6'] = 1 if current_price > sma_6 else -1
            signals['above_sma_11'] = 2 if current_price > sma_11 else -2  
            signals['above_sma_21'] = 3 if current_price > sma_21 else -3
            
            return signals
        except Exception as e:
            logger.error(f"Error calculating SMA signals for crypto {cryptocurrency_id}: {e}")
            raise
    
    def get_strong_coins_above_all_sma(self, target_date: date) -> List[str]:
        """Get coins that are above all SMAs on a specific date."""
        try:
            query = self.session.query(
                Cryptocurrency.coin_id
            ).join(
                SMAIndicator,
                SMAIndicator.cryptocurrency_id == Cryptocurrency.id
            ).filter(
                and_(
                    SMAIndicator.date == target_date,
                    SMAIndicator.above_sma_6 > 0,
                    SMAIndicator.above_sma_11 > 0,
                    SMAIndicator.above_sma_21 > 0
                )
            )
            
            return [coin[0] for coin in query.all()]
        except SQLAlchemyError as e:
            logger.error(f"Error getting strong coins above all SMA: {e}")
            raise