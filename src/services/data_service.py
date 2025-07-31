"""Data service for managing cryptocurrency data operations."""

from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional
import pandas as pd
import asyncio

from loguru import logger

from database.connection import DatabaseTransaction
from repositories import (
    CryptocurrencyRepository, 
    HistoricalPriceRepository, 
    SMAIndicatorRepository,
    CacheRepository
)
from services.coingecko_service import CoinGeckoService


class DataService:
    """Service for cryptocurrency data operations."""
    
    def __init__(self):
        self.cache_ttl = 3600  # 1 hour default cache
        self.coingecko_service = CoinGeckoService()
    
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
    
    async def populate_coins_from_coingecko(self, number_coins: int = 100) -> Dict[str, Any]:
        """Populate database with top coins from CoinGecko by market cap."""
        logger.info(f"Fetching top {number_coins} coins from CoinGecko by market cap")
        
        try:
            # Fetch coins data from CoinGecko
            coins_data = await self.coingecko_service.get_top_coins_by_market_cap(
                limit=number_coins,
                vs_currency='btc'
            )
            
            if not coins_data:
                logger.warning("No coins data received from CoinGecko")
                return {'success': False, 'error': 'No data received'}
            
            # Store coins in database
            with DatabaseTransaction() as session:
                crypto_repo = CryptocurrencyRepository(session)
                added_count = 0
                updated_count = 0
                
                for coin_data in coins_data:
                    coin_id = coin_data.get('id')
                    if not coin_id:
                        continue
                    
                    # Check if coin exists
                    existing_crypto = crypto_repo.get_by_coin_id(coin_id)
                    
                    if existing_crypto:
                        # Update existing
                        existing_crypto.name = coin_data.get('name', existing_crypto.name)
                        existing_crypto.symbol = coin_data.get('symbol', existing_crypto.symbol)
                        existing_crypto.market_cap_rank = coin_data.get('market_cap_rank')
                        existing_crypto.is_active = True
                        updated_count += 1
                    else:
                        # Create new
                        new_crypto = crypto_repo.create(
                            coin_id=coin_id,
                            name=coin_data.get('name', coin_id),
                            symbol=coin_data.get('symbol', coin_id.upper()),
                            market_cap_rank=coin_data.get('market_cap_rank'),
                            is_active=True
                        )
                        added_count += 1
                
                session.commit()
                
                logger.info(f"CoinGecko import completed: {added_count} added, {updated_count} updated")
                
                return {
                    'success': True,
                    'added': added_count,
                    'updated': updated_count,
                    'total': added_count + updated_count
                }
                
        except Exception as e:
            logger.error(f"Error populating coins from CoinGecko: {e}")
            return {'success': False, 'error': str(e)}
    
    def populate_coins_from_binance(self) -> Dict[str, Any]:
        """Populate database with BTC pairs from Binance."""
        logger.info("Fetching BTC pairs from Binance")
        
        try:
            # Import here to avoid issues if Binance API is not configured
            from binance import Client
            from config.settings import get_api_config
            
            api_config = get_api_config()
            
            if not api_config.binance_api_key or not api_config.binance_secret_key:
                return {'success': False, 'error': 'Binance API keys not configured'}
            
            client = Client(api_config.binance_api_key, api_config.binance_secret_key)
            exchange_info = client.get_exchange_info()
            
            btc_pairs = []
            for symbol_info in exchange_info['symbols']:
                if symbol_info["quoteAsset"] == 'BTC' and symbol_info['status'] == 'TRADING':
                    btc_pairs.append({
                        'symbol': symbol_info['symbol'],
                        'base_asset': symbol_info['baseAsset'],
                        'quote_asset': symbol_info['quoteAsset'],
                        'is_active': True
                    })
            
            logger.info(f"Found {len(btc_pairs)} BTC pairs on Binance")
            
            # Store in database
            with DatabaseTransaction() as session:
                crypto_repo = CryptocurrencyRepository(session)
                added_count = 0
                updated_count = 0
                
                for pair_data in btc_pairs:
                    # Use base asset as coin_id (remove BTC suffix from symbol)
                    base_asset = pair_data['base_asset'].lower()
                    symbol = pair_data['symbol']
                    
                    # Check if coin exists
                    existing_crypto = crypto_repo.get_by_coin_id(base_asset)
                    
                    if existing_crypto:
                        # Update existing
                        existing_crypto.symbol = pair_data['base_asset']
                        existing_crypto.is_active = True
                        updated_count += 1
                    else:
                        # Create new
                        new_crypto = crypto_repo.create(
                            coin_id=base_asset,
                            name=pair_data['base_asset'],
                            symbol=pair_data['base_asset'],
                            is_active=True
                        )
                        added_count += 1
                
                session.commit()
                
                logger.info(f"Binance import completed: {added_count} added, {updated_count} updated")
                
                return {
                    'success': True,
                    'added': added_count,
                    'updated': updated_count,
                    'total': added_count + updated_count
                }
                
        except Exception as e:
            logger.error(f"Error populating coins from Binance: {e}")
            return {'success': False, 'error': str(e)}
    
    async def fetch_and_store_historical_data(self, coin_ids: List[str], days: int = 30) -> Dict[str, Any]:
        """Fetch and store historical data for given coins."""
        logger.info(f"Fetching historical data for {len(coin_ids)} coins, {days} days")
        
        try:
            # Fetch data using CoinGecko service
            results = await self.coingecko_service.fetch_multiple_historical_data(
                coin_ids=coin_ids,
                days=days,
                vs_currency='btc'
            )
            
            stored_count = 0
            error_count = 0
            
            with DatabaseTransaction() as session:
                crypto_repo = CryptocurrencyRepository(session)
                price_repo = HistoricalPriceRepository(session)
                sma_repo = SMAIndicatorRepository(session)
                
                for coin_id, coin_data in results.items():
                    if not coin_data.get('success'):
                        error_count += 1
                        continue
                    
                    # Get cryptocurrency record
                    crypto = crypto_repo.get_by_coin_id(coin_id)
                    if not crypto:
                        logger.warning(f"Cryptocurrency {coin_id} not found in database")
                        error_count += 1
                        continue
                    
                    # Store price data
                    prices_data = coin_data.get('prices', [])
                    for price_entry in prices_data:
                        price_date = price_entry['date']
                        price_btc = price_entry['price_btc']
                        market_cap = price_entry.get('market_cap')
                        volume = price_entry.get('volume')
                        
                        # Ensure date is a Python date object
                        if isinstance(price_date, str):
                            price_date = datetime.strptime(price_date, '%Y-%m-%d').date()
                        
                        # Create or update price record (BTC denominated)
                        price_repo.create_or_update_price(
                            cryptocurrency_id=crypto.id,
                            date=price_date,
                            price_btc=price_btc
                            # Note: market_cap and volume from CoinGecko are in BTC when vs_currency='btc'
                            # but we have only USD fields in database, so we skip them for now
                        )
                    
                    # Calculate and store SMA indicators
                    if prices_data:
                        self._calculate_and_store_sma_indicators(
                            sma_repo, crypto.id, prices_data
                        )
                    
                    stored_count += 1
                
                session.commit()
            
            logger.info(f"Historical data fetch completed: {stored_count} coins processed, {error_count} errors")
            
            return {
                'success': True,
                'processed': stored_count,
                'errors': error_count,
                'total_coins': len(coin_ids)
            }
            
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            return {'success': False, 'error': str(e)}
    
    def _calculate_and_store_sma_indicators(self, sma_repo, crypto_id: int, prices_data: List[Dict]):
        """Calculate and store SMA indicators for price data."""
        try:
            # Convert to DataFrame for SMA calculation
            df = pd.DataFrame(prices_data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            df.set_index('date', inplace=True)
            
            # Calculate SMAs for all periods
            sma_6 = df['price_btc'].rolling(window=6).mean()
            sma_11 = df['price_btc'].rolling(window=11).mean()
            sma_21 = df['price_btc'].rolling(window=21).mean()
            
            # Calculate above SMA signals
            above_sma_6 = (df['price_btc'] > sma_6).replace({True: 1, False: -1})
            above_sma_11 = (df['price_btc'] > sma_11).replace({True: 2, False: -2})
            above_sma_21 = (df['price_btc'] > sma_21).replace({True: 3, False: -3})
            
            # Store SMA indicators for each date
            for date_idx in df.index:
                if pd.notna(sma_6.get(date_idx)) or pd.notna(sma_11.get(date_idx)) or pd.notna(sma_21.get(date_idx)):
                    
                    # Ensure date is a Python date object
                    target_date = date_idx.date() if hasattr(date_idx, 'date') else date_idx
                    
                    sma_data = {}
                    
                    # Add SMA values if available
                    if pd.notna(sma_6.get(date_idx)):
                        sma_data['sma_6'] = float(sma_6.get(date_idx))
                        sma_data['above_sma_6'] = int(above_sma_6.get(date_idx, 0))
                    
                    if pd.notna(sma_11.get(date_idx)):
                        sma_data['sma_11'] = float(sma_11.get(date_idx))
                        sma_data['above_sma_11'] = int(above_sma_11.get(date_idx, 0))
                    
                    if pd.notna(sma_21.get(date_idx)):
                        sma_data['sma_21'] = float(sma_21.get(date_idx))
                        sma_data['above_sma_21'] = int(above_sma_21.get(date_idx, 0))
                    
                    # Store using the existing method
                    if sma_data:
                        sma_repo.create_or_update_sma(
                            cryptocurrency_id=crypto_id,
                            date=target_date,
                            **sma_data
                        )
                            
        except Exception as e:
            logger.error(f"Error calculating SMA indicators: {e}")
    
    def get_available_data_sources(self) -> Dict[str, Any]:
        """Get information about available data sources."""
        from config.settings import get_api_config
        
        api_config = get_api_config()
        
        sources = {
            'coingecko': {
                'available': True,  # CoinGecko works without API key for basic calls
                'description': 'Top cryptocurrencies by market cap',
                'max_coins': 1000,
                'data_quality': 'High (with API key) / Medium (without API key)',
                'has_api_key': bool(api_config.coingecko_api_key and api_config.coingecko_api_key != "your_coingecko_api_key_here")
            },
            'binance': {
                'available': bool(api_config.binance_api_key and api_config.binance_secret_key and 
                                api_config.binance_api_key != "your_binance_api_key_here"),
                'description': 'All BTC trading pairs on Binance',
                'max_coins': 'All available pairs',
                'data_quality': 'High'
            }
        }
        
        return sources