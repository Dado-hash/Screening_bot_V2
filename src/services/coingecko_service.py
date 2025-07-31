"""CoinGecko API service with caching and error handling."""

import asyncio
import time
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Any, Optional

import aiohttp
from asyncio_throttle import Throttler
from pycoingecko import CoinGeckoAPI
from loguru import logger

from database.connection import DatabaseTransaction
from repositories import CryptocurrencyRepository, HistoricalPriceRepository, CacheRepository


class CoinGeckoService:
    """Service for fetching data from CoinGecko API with database storage."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.cg = CoinGeckoAPI(api_key=api_key)
        self.throttler = Throttler(rate_limit=14, period=60)  # 14 requests per minute for free API
        
        # Cache TTL settings
        self.market_data_ttl = 3600  # 1 hour
        self.historical_data_ttl = 86400  # 24 hours
    
    async def fetch_top_cryptocurrencies(self, limit: int = 100, vs_currency: str = 'btc') -> List[Dict[str, Any]]:
        """Fetch top cryptocurrencies by market cap."""
        cache_key = f"top_cryptos_{limit}_{vs_currency}"
        
        with DatabaseTransaction() as session:
            cache_repo = CacheRepository(session)
            
            # Try cache first
            cached_data = cache_repo.get_cached_value(cache_key)
            if cached_data:
                logger.debug(f"Using cached data for top {limit} cryptocurrencies")
                return cached_data
            
            # Fetch fresh data
            logger.info(f"Fetching top {limit} cryptocurrencies from CoinGecko")
            
            try:
                # Handle pagination for large requests
                all_cryptos = []
                pages_needed = (limit // 100) + (1 if limit % 100 > 0 else 0)
                
                for page in range(1, pages_needed + 1):
                    per_page = min(100, limit - len(all_cryptos))
                    
                    async with self.throttler:
                        response = self.cg.get_coins_markets(
                            vs_currency=vs_currency,
                            order='market_cap_desc',
                            per_page=per_page,
                            page=page,
                            price_change_percentage='24h'
                        )
                        
                        all_cryptos.extend(response)
                        
                        if len(all_cryptos) >= limit:
                            break
                        
                        # Rate limiting delay
                        await asyncio.sleep(5)
                
                # Cache the result
                cache_repo.set_cached_value(cache_key, all_cryptos, self.market_data_ttl, 'market_data')
                
                logger.info(f"Successfully fetched {len(all_cryptos)} cryptocurrencies")
                return all_cryptos
                
            except Exception as e:
                logger.error(f"Error fetching top cryptocurrencies: {e}")
                raise
    
    async def fetch_historical_data(self, coin_id: str, vs_currency: str = 'btc', 
                                  days: int = 365) -> List[Dict[str, Any]]:
        """Fetch historical price data for a cryptocurrency."""
        cache_key = f"historical_{coin_id}_{vs_currency}_{days}"
        
        with DatabaseTransaction() as session:
            cache_repo = CacheRepository(session)
            
            # Try cache first
            cached_data = cache_repo.get_cached_value(cache_key)
            if cached_data:
                logger.debug(f"Using cached historical data for {coin_id}")
                return cached_data
            
            # Fetch fresh data
            logger.info(f"Fetching historical data for {coin_id} ({days} days)")
            
            try:
                async with self.throttler:
                    response = self.cg.get_coin_market_chart_by_id(
                        id=coin_id,
                        vs_currency=vs_currency,
                        days=days if days <= 90 else 'max',
                        interval='daily'
                    )
                
                # Process the response
                historical_data = []
                prices = response.get('prices', [])
                volumes = response.get('total_volumes', [])
                market_caps = response.get('market_caps', [])
                
                for i, price_data in enumerate(prices):
                    timestamp, price = price_data
                    price_date = datetime.fromtimestamp(timestamp / 1000).date()
                    
                    # Skip today's incomplete data
                    if price_date >= date.today():
                        continue
                    
                    data_point = {
                        'date': price_date,
                        'price': float(price),
                        'volume': float(volumes[i][1]) if i < len(volumes) else None,
                        'market_cap': float(market_caps[i][1]) if i < len(market_caps) else None
                    }
                    
                    historical_data.append(data_point)
                
                # Cache the result
                cache_repo.set_cached_value(cache_key, historical_data, self.historical_data_ttl, 'historical_data')
                
                logger.info(f"Successfully fetched {len(historical_data)} historical data points for {coin_id}")
                return historical_data
                
            except Exception as e:
                logger.error(f"Error fetching historical data for {coin_id}: {e}")
                raise
    
    async def store_cryptocurrencies_to_db(self, crypto_data: List[Dict[str, Any]]) -> int:
        """Store cryptocurrency data to database."""
        logger.info(f"Storing {len(crypto_data)} cryptocurrencies to database")
        
        with DatabaseTransaction() as session:
            crypto_repo = CryptocurrencyRepository(session)
            
            processed_data = []
            for crypto in crypto_data:
                processed_crypto = {
                    'coin_id': crypto['id'],
                    'name': crypto['name'],
                    'symbol': crypto['symbol'].upper(),
                    'market_cap_rank': crypto.get('market_cap_rank'),
                    'is_active': True
                }
                processed_data.append(processed_crypto)
            
            # Bulk create or update
            result = crypto_repo.bulk_create_or_update(processed_data)
            
            logger.info(f"Successfully stored {len(result)} cryptocurrencies")
            return len(result)
    
    async def store_historical_data_to_db(self, coin_id: str, historical_data: List[Dict[str, Any]], 
                                        vs_currency: str = 'btc') -> int:
        """Store historical price data to database."""
        logger.info(f"Storing {len(historical_data)} historical data points for {coin_id}")
        
        with DatabaseTransaction() as session:
            crypto_repo = CryptocurrencyRepository(session)
            price_repo = HistoricalPriceRepository(session)
            
            # Get or create cryptocurrency
            crypto = crypto_repo.get_by_coin_id(coin_id)
            if not crypto:
                logger.warning(f"Cryptocurrency {coin_id} not found in database")
                return 0
            
            # Prepare price records
            price_records = []
            for data_point in historical_data:
                price_record = {
                    'cryptocurrency_id': crypto.id,
                    'date': data_point['date'],
                    'volume_usd': Decimal(str(data_point['volume'])) if data_point.get('volume') else None,
                    'market_cap_usd': Decimal(str(data_point['market_cap'])) if data_point.get('market_cap') else None
                }
                
                # Set price in appropriate currency
                if vs_currency == 'btc':
                    price_record['price_btc'] = Decimal(str(data_point['price']))
                else:
                    price_record['price_usd'] = Decimal(str(data_point['price']))
                
                price_records.append(price_record)
            
            # Bulk upsert
            updated_count = price_repo.bulk_upsert_prices(price_records)
            
            logger.info(f"Successfully stored {updated_count} price records for {coin_id}")
            return updated_count
    
    async def calculate_and_store_sma(self, coin_id: str, window_days: int = 90) -> int:
        """Calculate and store SMA indicators for a cryptocurrency."""
        logger.info(f"Calculating SMA indicators for {coin_id}")
        
        with DatabaseTransaction() as session:
            crypto_repo = CryptocurrencyRepository(session)
            price_repo = HistoricalPriceRepository(session)
            
            # Get cryptocurrency
            crypto = crypto_repo.get_by_coin_id(coin_id)
            if not crypto:
                logger.warning(f"Cryptocurrency {coin_id} not found")
                return 0
            
            # Get historical prices for SMA calculation
            end_date = date.today()
            start_date = end_date - timedelta(days=window_days + 21)  # Extra days for SMA calculation
            
            prices = price_repo.get_price_range(crypto.id, start_date, end_date)
            
            if len(prices) < 21:  # Need at least 21 days for SMA21
                logger.warning(f"Insufficient price data for {coin_id} SMA calculation")
                return 0
            
            # Convert to pandas DataFrame for easier calculation
            import pandas as pd
            
            df = pd.DataFrame([{
                'date': p.date,
                'price_btc': float(p.price_btc) if p.price_btc else None
            } for p in prices])
            
            df = df.dropna().sort_values('date')
            
            # Calculate SMAs
            df['sma_6'] = df['price_btc'].rolling(window=6, min_periods=6).mean()
            df['sma_11'] = df['price_btc'].rolling(window=11, min_periods=11).mean()
            df['sma_21'] = df['price_btc'].rolling(window=21, min_periods=21).mean()
            
            # Calculate above SMA signals
            df['above_sma_6'] = df.apply(lambda row: 1 if row['price_btc'] > row['sma_6'] else -1, axis=1)
            df['above_sma_11'] = df.apply(lambda row: 2 if row['price_btc'] > row['sma_11'] else -2, axis=1)
            df['above_sma_21'] = df.apply(lambda row: 3 if row['price_btc'] > row['sma_21'] else -3, axis=1)
            
            # Store SMA data
            from repositories import SMAIndicatorRepository
            sma_repo = SMAIndicatorRepository(session)
            
            sma_records = []
            for _, row in df.dropna().iterrows():
                sma_record = {
                    'cryptocurrency_id': crypto.id,
                    'date': row['date'],
                    'sma_6': Decimal(str(row['sma_6'])),
                    'sma_11': Decimal(str(row['sma_11'])),
                    'sma_21': Decimal(str(row['sma_21'])),
                    'above_sma_6': int(row['above_sma_6']),
                    'above_sma_11': int(row['above_sma_11']),
                    'above_sma_21': int(row['above_sma_21'])
                }
                sma_records.append(sma_record)
            
            updated_count = sma_repo.bulk_upsert_sma(sma_records)
            
            logger.info(f"Successfully calculated and stored {updated_count} SMA records for {coin_id}")
            return updated_count
    
    async def sync_all_data(self, coin_limit: int = 100, days: int = 365) -> Dict[str, int]:
        """Sync all cryptocurrency data from CoinGecko to database."""
        logger.info(f"Starting full data sync for {coin_limit} cryptocurrencies")
        
        stats = {
            'cryptocurrencies_synced': 0,
            'price_records_synced': 0,
            'sma_records_synced': 0,
            'errors': 0
        }
        
        try:
            # 1. Fetch and store cryptocurrency list
            crypto_data = await self.fetch_top_cryptocurrencies(coin_limit)
            stats['cryptocurrencies_synced'] = await self.store_cryptocurrencies_to_db(crypto_data)
            
            # 2. Fetch historical data for each cryptocurrency
            for i, crypto in enumerate(crypto_data[:coin_limit]):
                coin_id = crypto['id']
                
                try:
                    logger.info(f"Processing {coin_id} ({i+1}/{coin_limit})")
                    
                    # Fetch and store historical prices (BTC)
                    historical_data = await self.fetch_historical_data(coin_id, 'btc', days)
                    price_count = await self.store_historical_data_to_db(coin_id, historical_data, 'btc')
                    stats['price_records_synced'] += price_count
                    
                    # Calculate and store SMA indicators
                    sma_count = await self.calculate_and_store_sma(coin_id)
                    stats['sma_records_synced'] += sma_count
                    
                    # Rate limiting between coins
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Error processing {coin_id}: {e}")
                    stats['errors'] += 1
                    continue
            
            logger.info(f"Data sync completed: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Critical error in data sync: {e}")
            raise