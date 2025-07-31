"""Data service for managing cryptocurrency data operations."""

from datetime import date, timedelta
from typing import List, Dict, Any, Optional
import pandas as pd

from loguru import logger

from database.connection import DatabaseTransaction
from repositories import (
    CryptocurrencyRepository, 
    HistoricalPriceRepository, 
    SMAIndicatorRepository,
    CacheRepository
)


class DataService:
    """Service for cryptocurrency data operations."""
    
    def __init__(self):
        self.cache_ttl = 3600  # 1 hour default cache
    
    def get_active_cryptocurrencies(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get list of active cryptocurrencies."""
        with DatabaseTransaction() as session:
            crypto_repo = CryptocurrencyRepository(session)
            cryptos = crypto_repo.get_active_cryptocurrencies(limit)
            
            return [{
                'id': crypto.id,
                'coin_id': crypto.coin_id,
                'name': crypto.name,
                'symbol': crypto.symbol,
                'market_cap_rank': crypto.market_cap_rank
            } for crypto in cryptos]
    
    def get_price_dataframe(self, coin_ids: List[str], days: int = 30, 
                           price_column: str = 'price_btc') -> pd.DataFrame:
        """Get price data as DataFrame for analysis."""
        cache_key = f"price_df_{hash(str(sorted(coin_ids)))}_{days}_{price_column}"
        
        with DatabaseTransaction() as session:
            cache_repo = CacheRepository(session)
            price_repo = HistoricalPriceRepository(session)
            
            # Try cache first
            cached_df = cache_repo.get_cached_value(cache_key)
            if cached_df is not None:
                logger.debug(f"Using cached price DataFrame for {len(coin_ids)} coins")
                return pd.DataFrame(cached_df)
            
            # Fetch fresh data
            logger.info(f"Creating price DataFrame for {len(coin_ids)} coins, {days} days")
            df = price_repo.get_price_history_dataframe(coin_ids, days, price_column)
            
            # Cache the result (convert to dict for JSON serialization)
            cache_repo.set_cached_value(cache_key, df.to_dict(), self.cache_ttl, 'dataframe')
            
            return df
    
    def get_sma_dataframe(self, coin_ids: List[str], days: int = 30, 
                         sma_period: str = 'sma_6') -> pd.DataFrame:
        """Get SMA data as DataFrame."""
        cache_key = f"sma_df_{hash(str(sorted(coin_ids)))}_{days}_{sma_period}"
        
        with DatabaseTransaction() as session:
            cache_repo = CacheRepository(session)
            sma_repo = SMAIndicatorRepository(session)
            
            # Try cache first
            cached_df = cache_repo.get_cached_value(cache_key)
            if cached_df is not None:
                logger.debug(f"Using cached SMA DataFrame")
                return pd.DataFrame(cached_df)
            
            # Fetch fresh data
            logger.info(f"Creating SMA DataFrame for {len(coin_ids)} coins")
            df = sma_repo.get_sma_dataframe(coin_ids, days, sma_period)
            
            # Cache the result
            cache_repo.set_cached_value(cache_key, df.to_dict(), self.cache_ttl, 'dataframe')
            
            return df
    
    def get_above_sma_dataframe(self, coin_ids: List[str], days: int = 30, 
                               sma_signal: str = 'above_sma_6') -> pd.DataFrame:
        """Get above SMA signals as DataFrame."""
        cache_key = f"above_sma_df_{hash(str(sorted(coin_ids)))}_{days}_{sma_signal}"
        
        with DatabaseTransaction() as session:
            cache_repo = CacheRepository(session)
            sma_repo = SMAIndicatorRepository(session)
            
            # Try cache first
            cached_df = cache_repo.get_cached_value(cache_key)
            if cached_df is not None:
                logger.debug(f"Using cached above SMA DataFrame")
                return pd.DataFrame(cached_df)
            
            # Fetch fresh data
            logger.info(f"Creating above SMA DataFrame for {len(coin_ids)} coins")
            df = sma_repo.get_above_sma_dataframe(coin_ids, days, sma_signal)
            
            # Cache the result
            cache_repo.set_cached_value(cache_key, df.to_dict(), self.cache_ttl, 'dataframe')
            
            return df
    
    def calculate_cumulative_returns(self, coin_ids: List[str], days_back: int, 
                                   direction: str = 'backward') -> pd.DataFrame:
        """Calculate cumulative returns for screening analysis."""
        logger.info(f"Calculating cumulative returns for {len(coin_ids)} coins, {days_back} days {direction}")
        
        # Get price data
        df_prices = self.get_price_dataframe(coin_ids, days_back + 10, 'price_btc')  # Extra days for calculation
        
        if df_prices.empty:
            logger.warning("No price data available for calculation")
            return pd.DataFrame()
        
        # Calculate returns based on direction
        results = {}
        
        if direction == 'backward':
            # From today going backward
            for days in range(1, days_back + 1):
                if len(df_prices) >= days:
                    # Calculate percentage change
                    latest_prices = df_prices.iloc[-1]  # Most recent
                    past_prices = df_prices.iloc[-(days + 1)]  # N days ago
                    
                    # Calculate cumulative return
                    cumulative_returns = ((latest_prices - past_prices) / past_prices * 100).dropna()
                    results[f'{days}d'] = cumulative_returns.sort_values(ascending=False)
        
        else:  # forward
            # From a specific day going forward
            start_idx = len(df_prices) - days_back - 1
            if start_idx >= 0:
                for days in range(1, days_back + 1):
                    end_idx = start_idx + days
                    if end_idx < len(df_prices):
                        start_prices = df_prices.iloc[start_idx]
                        end_prices = df_prices.iloc[end_idx]
                        
                        cumulative_returns = ((end_prices - start_prices) / start_prices * 100).dropna()
                        results[f'{days}d'] = cumulative_returns.sort_values(ascending=False)
        
        # Convert to DataFrame
        if results:
            result_df = pd.DataFrame(results)
            result_df = result_df.fillna(0)
            return result_df
        else:
            return pd.DataFrame()
    
    def get_data_coverage_stats(self) -> Dict[str, Any]:
        """Get statistics about data coverage."""
        with DatabaseTransaction() as session:
            crypto_repo = CryptocurrencyRepository(session)
            price_repo = HistoricalPriceRepository(session)
            sma_repo = SMAIndicatorRepository(session)
            
            stats = {
                'total_cryptocurrencies': crypto_repo.count(),
                'active_cryptocurrencies': len(crypto_repo.get_active_cryptocurrencies()),
                'total_price_records': price_repo.count(),
                'total_sma_records': sma_repo.count(),
                'latest_prices': [],
                'data_gaps': []
            }
            
            # Get some latest prices for sample
            latest_prices = price_repo.get_latest_prices(limit=10)
            stats['latest_prices'] = [{
                'coin_id': price.cryptocurrency.coin_id,
                'date': price.date.isoformat(),
                'price_btc': float(price.price_btc) if price.price_btc else None
            } for price in latest_prices]
            
            return stats
    
    def cleanup_old_data(self, days_to_keep: int = 365) -> Dict[str, int]:
        """Clean up old data to save space."""
        cutoff_date = date.today() - timedelta(days=days_to_keep)
        
        with DatabaseTransaction() as session:
            price_repo = HistoricalPriceRepository(session)
            sma_repo = SMAIndicatorRepository(session)
            cache_repo = CacheRepository(session)
            
            # Clean up old price records (keep recent data)
            old_prices = session.query(price_repo.model).filter(
                price_repo.model.date < cutoff_date
            ).count()
            
            # Clean up expired cache entries
            expired_cache = cache_repo.cleanup_expired_entries()
            
            logger.info(f"Cleanup completed: {old_prices} old prices, {expired_cache} expired cache entries")
            
            return {
                'old_price_records': old_prices,
                'expired_cache_entries': expired_cache
            }
    
    def export_data_to_excel(self, coin_ids: List[str], days: int = 30, 
                           output_path: str = 'data/outputs/exported_data.xlsx') -> bool:
        """Export data to Excel format for compatibility."""
        try:
            logger.info(f"Exporting data for {len(coin_ids)} coins to {output_path}")
            
            # Get various data types
            price_df = self.get_price_dataframe(coin_ids, days, 'price_btc')
            sma_fast_df = self.get_above_sma_dataframe(coin_ids, days, 'above_sma_6')
            sma_medium_df = self.get_above_sma_dataframe(coin_ids, days, 'above_sma_11')
            sma_slow_df = self.get_above_sma_dataframe(coin_ids, days, 'above_sma_21')
            
            # Create cumulative returns
            cumulative_df = self.calculate_cumulative_returns(coin_ids, days)
            
            # Export to Excel with multiple sheets
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                if not price_df.empty:
                    price_df.to_excel(writer, sheet_name='closes')
                if not sma_fast_df.empty:
                    sma_fast_df.to_excel(writer, sheet_name='above_fast')
                if not sma_medium_df.empty:
                    sma_medium_df.to_excel(writer, sheet_name='above_medium')
                if not sma_slow_df.empty:
                    sma_slow_df.to_excel(writer, sheet_name='above_slow')
                if not cumulative_df.empty:
                    cumulative_df.to_excel(writer, sheet_name='cumulatives')
            
            logger.info(f"Data exported successfully to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting data to Excel: {e}")
            return False