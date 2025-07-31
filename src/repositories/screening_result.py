"""Repository for screening result operations."""

from datetime import date, timedelta
from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, desc, asc, func
from loguru import logger
import pandas as pd

from .base import BaseRepository
from ..database.models import ScreeningResult, Cryptocurrency


class ScreeningResultRepository(BaseRepository[ScreeningResult]):
    """Repository for screening result operations."""
    
    def __init__(self, session: Session):
        super().__init__(session, ScreeningResult)
    
    def get_by_crypto_date_timeframe(self, cryptocurrency_id: int, analysis_date: date, 
                                   timeframe_days: int, direction: str) -> Optional[ScreeningResult]:
        """Get screening result for specific parameters."""
        try:
            return self.session.query(ScreeningResult).filter(
                and_(
                    ScreeningResult.cryptocurrency_id == cryptocurrency_id,
                    ScreeningResult.analysis_date == analysis_date,
                    ScreeningResult.timeframe_days == timeframe_days,
                    ScreeningResult.direction == direction
                )
            ).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting screening result: {e}")
            raise
    
    def get_results_for_date(self, analysis_date: date, direction: str = 'forward') -> List[ScreeningResult]:
        """Get all screening results for a specific analysis date."""
        try:
            return self.session.query(ScreeningResult).filter(
                and_(
                    ScreeningResult.analysis_date == analysis_date,
                    ScreeningResult.direction == direction
                )
            ).options(joinedload(ScreeningResult.cryptocurrency)).all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting results for date {analysis_date}: {e}")
            raise
    
    def get_top_performers(self, analysis_date: date, direction: str = 'forward', 
                         timeframe_days: int = 1, limit: int = 20) -> List[ScreeningResult]:
        """Get top performing cryptocurrencies by total score."""
        try:
            return self.session.query(ScreeningResult).filter(
                and_(
                    ScreeningResult.analysis_date == analysis_date,
                    ScreeningResult.direction == direction,
                    ScreeningResult.timeframe_days == timeframe_days
                )
            ).options(
                joinedload(ScreeningResult.cryptocurrency)
            ).order_by(
                desc(ScreeningResult.total_score)
            ).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting top performers: {e}")
            raise
    
    def get_results_dataframe(self, analysis_date: date, direction: str = 'forward') -> pd.DataFrame:
        """Get screening results as pandas DataFrame for analysis."""
        try:
            query = self.session.query(
                Cryptocurrency.coin_id,
                Cryptocurrency.name,
                Cryptocurrency.symbol,
                ScreeningResult.timeframe_days,
                ScreeningResult.cumulative_return,
                ScreeningResult.rank_position,
                ScreeningResult.rank_change,
                ScreeningResult.total_score,
                ScreeningResult.day_rank_score,
                ScreeningResult.sma_fast_score,
                ScreeningResult.sma_medium_score,
                ScreeningResult.sma_slow_score
            ).join(
                Cryptocurrency,
                ScreeningResult.cryptocurrency_id == Cryptocurrency.id
            ).filter(
                and_(
                    ScreeningResult.analysis_date == analysis_date,
                    ScreeningResult.direction == direction
                )
            ).order_by(
                ScreeningResult.timeframe_days.asc(),
                desc(ScreeningResult.total_score)
            )
            
            df = pd.read_sql(query.statement, self.session.bind)
            return df
        except Exception as e:
            logger.error(f"Error creating screening results dataframe: {e}")
            raise
    
    def get_leaderboard_dataframe(self, analysis_date: date, direction: str = 'forward') -> pd.DataFrame:
        """Get leaderboard with cumulative returns for different timeframes."""
        try:
            query = self.session.query(
                Cryptocurrency.coin_id,
                ScreeningResult.timeframe_days,
                ScreeningResult.cumulative_return
            ).join(
                Cryptocurrency,
                ScreeningResult.cryptocurrency_id == Cryptocurrency.id
            ).filter(
                and_(
                    ScreeningResult.analysis_date == analysis_date,
                    ScreeningResult.direction == direction
                )
            ).order_by(
                Cryptocurrency.coin_id,
                ScreeningResult.timeframe_days
            )
            
            df = pd.read_sql(query.statement, self.session.bind)
            
            # Pivot to have timeframes as columns
            df_pivot = df.pivot(index='coin_id', columns='timeframe_days', values='cumulative_return')
            df_pivot.columns = [f'{int(col)}d' for col in df_pivot.columns]
            
            return df_pivot
        except Exception as e:
            logger.error(f"Error creating leaderboard dataframe: {e}")
            raise
    
    def create_or_update_result(self, cryptocurrency_id: int, analysis_date: date,
                              timeframe_days: int, direction: str, **result_data) -> ScreeningResult:
        """Create new screening result or update existing one."""
        try:
            result = self.get_by_crypto_date_timeframe(
                cryptocurrency_id, analysis_date, timeframe_days, direction
            )
            
            if result:
                # Update existing
                for key, value in result_data.items():
                    if hasattr(result, key):
                        setattr(result, key, value)
                logger.debug(f"Updated screening result for crypto {cryptocurrency_id}")
            else:
                # Create new
                result = self.create(
                    cryptocurrency_id=cryptocurrency_id,
                    analysis_date=analysis_date,
                    timeframe_days=timeframe_days,
                    direction=direction,
                    **result_data
                )
                logger.debug(f"Created new screening result for crypto {cryptocurrency_id}")
            
            self.session.flush()
            return result
        except SQLAlchemyError as e:
            logger.error(f"Error creating/updating screening result: {e}")
            raise
    
    def bulk_upsert_results(self, result_records: List[Dict[str, Any]]) -> int:
        """Efficiently insert or update multiple screening results."""
        try:
            updated_count = 0
            
            for record in result_records:
                crypto_id = record['cryptocurrency_id']
                analysis_date = record['analysis_date']
                timeframe_days = record['timeframe_days']
                direction = record['direction']
                
                existing = self.get_by_crypto_date_timeframe(
                    crypto_id, analysis_date, timeframe_days, direction
                )
                
                if existing:
                    # Update existing record
                    for key, value in record.items():
                        if key not in ['cryptocurrency_id', 'analysis_date', 'timeframe_days', 'direction'] and hasattr(existing, key):
                            setattr(existing, key, value)
                else:
                    # Create new record
                    new_result = ScreeningResult(**record)
                    self.session.add(new_result)
                
                updated_count += 1
            
            self.session.flush()
            logger.debug(f"Bulk upserted {updated_count} screening result records")
            return updated_count
        except SQLAlchemyError as e:
            logger.error(f"Error in bulk upsert screening results: {e}")
            raise
    
    def get_historical_performance(self, coin_id: str, days: int = 30) -> pd.DataFrame:
        """Get historical screening performance for a specific coin."""
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            query = self.session.query(
                ScreeningResult.analysis_date,
                ScreeningResult.timeframe_days,
                ScreeningResult.direction,
                ScreeningResult.cumulative_return,
                ScreeningResult.total_score,
                ScreeningResult.rank_position
            ).join(
                Cryptocurrency,
                ScreeningResult.cryptocurrency_id == Cryptocurrency.id
            ).filter(
                and_(
                    Cryptocurrency.coin_id == coin_id,
                    ScreeningResult.analysis_date >= start_date,
                    ScreeningResult.analysis_date <= end_date
                )
            ).order_by(ScreeningResult.analysis_date.asc())
            
            df = pd.read_sql(query.statement, self.session.bind)
            df['analysis_date'] = pd.to_datetime(df['analysis_date'])
            
            return df
        except Exception as e:
            logger.error(f"Error getting historical performance for {coin_id}: {e}")
            raise
    
    def get_score_distribution(self, analysis_date: date, direction: str = 'forward') -> Dict[str, Any]:
        """Get score distribution statistics for an analysis date."""
        try:
            query = self.session.query(
                func.avg(ScreeningResult.total_score).label('avg_score'),
                func.min(ScreeningResult.total_score).label('min_score'),
                func.max(ScreeningResult.total_score).label('max_score'),
                func.count(ScreeningResult.id).label('total_count')
            ).filter(
                and_(
                    ScreeningResult.analysis_date == analysis_date,
                    ScreeningResult.direction == direction
                )
            )
            
            result = query.first()
            
            return {
                'avg_score': float(result.avg_score or 0),
                'min_score': float(result.min_score or 0),
                'max_score': float(result.max_score or 0),
                'total_count': int(result.total_count or 0)
            }
        except SQLAlchemyError as e:
            logger.error(f"Error getting score distribution: {e}")
            raise
    
    def cleanup_old_results(self, days_to_keep: int = 90) -> int:
        """Remove screening results older than specified days."""
        try:
            cutoff_date = date.today() - timedelta(days=days_to_keep)
            
            deleted_count = self.session.query(ScreeningResult).filter(
                ScreeningResult.analysis_date < cutoff_date
            ).delete()
            
            self.session.flush()
            logger.info(f"Cleaned up {deleted_count} old screening results")
            return deleted_count
        except SQLAlchemyError as e:
            logger.error(f"Error cleaning up old results: {e}")
            raise