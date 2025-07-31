"""Repository for historical price data operations."""

from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Any
from decimal import Decimal

from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, desc, asc, func
from loguru import logger
import pandas as pd

from src.repositories.base import BaseRepository
from src.database.models import HistoricalPrice, Cryptocurrency


class HistoricalPriceRepository(BaseRepository[HistoricalPrice]):
    """Repository for historical price operations."""
    
    def __init__(self, session: Session):
        super().__init__(session, HistoricalPrice)
    
    def get_by_crypto_and_date(self, cryptocurrency_id: int, date: date) -> Optional[HistoricalPrice]:
        """Get historical price for specific crypto and date."""
        try:
            return self.session.query(HistoricalPrice).filter(
                and_(
                    HistoricalPrice.cryptocurrency_id == cryptocurrency_id,
                    HistoricalPrice.date == date
                )
            ).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting historical price for crypto {cryptocurrency_id} on {date}: {e}")
            raise
    
    def get_price_range(self, cryptocurrency_id: int, start_date: date, end_date: date) -> List[HistoricalPrice]:
        """Get historical prices for a crypto within date range."""
        try:
            return self.session.query(HistoricalPrice).filter(
                and_(
                    HistoricalPrice.cryptocurrency_id == cryptocurrency_id,
                    HistoricalPrice.date >= start_date,
                    HistoricalPrice.date <= end_date
                )
            ).order_by(HistoricalPrice.date.asc()).all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting price range for crypto {cryptocurrency_id}: {e}")
            raise
    
    def get_latest_prices(self, limit: int = 100) -> List[HistoricalPrice]:
        """Get latest prices across all cryptocurrencies."""
        try:
            subquery = self.session.query(
                HistoricalPrice.cryptocurrency_id,
                func.max(HistoricalPrice.date).label('max_date')
            ).group_by(HistoricalPrice.cryptocurrency_id).subquery()
            
            return self.session.query(HistoricalPrice).join(
                subquery,
                and_(
                    HistoricalPrice.cryptocurrency_id == subquery.c.cryptocurrency_id,
                    HistoricalPrice.date == subquery.c.max_date
                )
            ).options(joinedload(HistoricalPrice.cryptocurrency)).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting latest prices: {e}")
            raise
    
    def get_prices_for_date(self, target_date: date) -> List[HistoricalPrice]:
        """Get all crypto prices for a specific date."""
        try:
            return self.session.query(HistoricalPrice).filter(
                HistoricalPrice.date == target_date
            ).options(joinedload(HistoricalPrice.cryptocurrency)).all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting prices for date {target_date}: {e}")
            raise
    
    def get_price_history_dataframe(self, coin_ids: List[str], days: int = 30, 
                                  price_column: str = 'price_btc') -> pd.DataFrame:
        """Get price history as pandas DataFrame for analysis."""
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            query = self.session.query(
                Cryptocurrency.coin_id,
                HistoricalPrice.date,
                getattr(HistoricalPrice, price_column)
            ).join(
                Cryptocurrency, 
                HistoricalPrice.cryptocurrency_id == Cryptocurrency.id
            ).filter(
                and_(
                    Cryptocurrency.coin_id.in_(coin_ids),
                    HistoricalPrice.date >= start_date,
                    HistoricalPrice.date <= end_date
                )
            ).order_by(HistoricalPrice.date.asc())
            
            df = pd.read_sql(query.statement, self.session.bind)
            
            # Pivot to have coins as columns and dates as index
            df_pivot = df.pivot(index='date', columns='coin_id', values=price_column)
            df_pivot.index = pd.to_datetime(df_pivot.index)
            
            return df_pivot
        except Exception as e:
            logger.error(f"Error creating price history dataframe: {e}")
            raise
    
    def create_or_update_price(self, cryptocurrency_id: int, date: date, **price_data) -> HistoricalPrice:
        """Create new price record or update existing one."""
        try:
            price = self.get_by_crypto_and_date(cryptocurrency_id, date)
            
            if price:
                # Update existing
                for key, value in price_data.items():
                    if hasattr(price, key):
                        setattr(price, key, value)
                logger.debug(f"Updated price for crypto {cryptocurrency_id} on {date}")
            else:
                # Create new
                price = self.create(
                    cryptocurrency_id=cryptocurrency_id,
                    date=date,
                    **price_data
                )
                logger.debug(f"Created new price for crypto {cryptocurrency_id} on {date}")
            
            self.session.flush()
            return price
        except SQLAlchemyError as e:
            logger.error(f"Error creating/updating price for crypto {cryptocurrency_id}: {e}")
            raise
    
    def bulk_upsert_prices(self, price_records: List[Dict[str, Any]]) -> int:
        """Efficiently insert or update multiple price records."""
        try:
            updated_count = 0
            
            for record in price_records:
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
                    new_price = HistoricalPrice(**record)
                    self.session.add(new_price)
                
                updated_count += 1
            
            self.session.flush()
            logger.debug(f"Bulk upserted {updated_count} price records")
            return updated_count
        except SQLAlchemyError as e:
            logger.error(f"Error in bulk upsert prices: {e}")
            raise
    
    def get_missing_dates(self, cryptocurrency_id: int, start_date: date, end_date: date) -> List[date]:
        """Get list of dates missing price data for a cryptocurrency."""
        try:
            existing_dates = self.session.query(HistoricalPrice.date).filter(
                and_(
                    HistoricalPrice.cryptocurrency_id == cryptocurrency_id,
                    HistoricalPrice.date >= start_date,
                    HistoricalPrice.date <= end_date
                )
            ).all()
            
            existing_dates_set = {d[0] for d in existing_dates}
            
            # Generate all dates in range
            all_dates = []
            current_date = start_date
            while current_date <= end_date:
                all_dates.append(current_date)
                current_date += timedelta(days=1)
            
            # Find missing dates
            missing_dates = [d for d in all_dates if d not in existing_dates_set]
            
            return missing_dates
        except SQLAlchemyError as e:
            logger.error(f"Error finding missing dates for crypto {cryptocurrency_id}: {e}")
            raise
    
    def get_crypto_performance(self, coin_ids: List[str], days: int) -> pd.DataFrame:
        """Calculate cumulative performance for cryptocurrencies over specified days."""
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            query = self.session.query(
                Cryptocurrency.coin_id,
                HistoricalPrice.date,
                HistoricalPrice.price_btc
            ).join(
                Cryptocurrency,
                HistoricalPrice.cryptocurrency_id == Cryptocurrency.id
            ).filter(
                and_(
                    Cryptocurrency.coin_id.in_(coin_ids),
                    HistoricalPrice.date >= start_date,
                    HistoricalPrice.date <= end_date,
                    HistoricalPrice.price_btc.isnot(None)
                )
            ).order_by(Cryptocurrency.coin_id, HistoricalPrice.date.asc())
            
            df = pd.read_sql(query.statement, self.session.bind)
            
            if df.empty:
                return df
            
            # Calculate percentage changes
            df['price_btc'] = df['price_btc'].astype(float)
            df = df.sort_values(['coin_id', 'date'])
            df['pct_change'] = df.groupby('coin_id')['price_btc'].pct_change()
            df['cumulative_return'] = df.groupby('coin_id')['pct_change'].cumsum()
            
            return df
        except Exception as e:
            logger.error(f"Error calculating crypto performance: {e}")
            raise