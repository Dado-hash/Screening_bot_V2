"""Repository for cryptocurrency data operations."""

from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger

from .base import BaseRepository
from ..database.models import Cryptocurrency


class CryptocurrencyRepository(BaseRepository[Cryptocurrency]):
    """Repository for cryptocurrency operations."""
    
    def __init__(self, session: Session):
        super().__init__(session, Cryptocurrency)
    
    def get_by_coin_id(self, coin_id: str) -> Optional[Cryptocurrency]:
        """Get cryptocurrency by coin_id (e.g., 'bitcoin', 'ethereum')."""
        try:
            return self.session.query(Cryptocurrency).filter(
                Cryptocurrency.coin_id == coin_id
            ).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting cryptocurrency by coin_id {coin_id}: {e}")
            raise
    
    def get_by_symbol(self, symbol: str) -> Optional[Cryptocurrency]:
        """Get cryptocurrency by symbol (e.g., 'BTC', 'ETH')."""
        try:
            return self.session.query(Cryptocurrency).filter(
                Cryptocurrency.symbol.ilike(symbol)
            ).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting cryptocurrency by symbol {symbol}: {e}")
            raise
    
    def get_active_cryptocurrencies(self, limit: Optional[int] = None) -> List[Cryptocurrency]:
        """Get all active cryptocurrencies ordered by market cap rank."""
        try:
            query = self.session.query(Cryptocurrency).filter(
                Cryptocurrency.is_active == True
            ).order_by(Cryptocurrency.market_cap_rank.asc().nulls_last())
            
            if limit:
                query = query.limit(limit)
                
            return query.all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting active cryptocurrencies: {e}")
            raise
    
    def get_by_coin_ids(self, coin_ids: List[str]) -> List[Cryptocurrency]:
        """Get multiple cryptocurrencies by coin_ids."""
        try:
            return self.session.query(Cryptocurrency).filter(
                Cryptocurrency.coin_id.in_(coin_ids)
            ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting cryptocurrencies by coin_ids: {e}")
            raise
    
    def create_or_update(self, coin_id: str, **kwargs) -> Cryptocurrency:
        """Create new cryptocurrency or update existing one."""
        try:
            crypto = self.get_by_coin_id(coin_id)
            
            if crypto:
                # Update existing
                for key, value in kwargs.items():
                    if hasattr(crypto, key):
                        setattr(crypto, key, value)
                logger.debug(f"Updated cryptocurrency {coin_id}")
            else:
                # Create new
                crypto = self.create(coin_id=coin_id, **kwargs)
                logger.debug(f"Created new cryptocurrency {coin_id}")
            
            self.session.flush()
            return crypto
        except SQLAlchemyError as e:
            logger.error(f"Error creating/updating cryptocurrency {coin_id}: {e}")
            raise
    
    def bulk_create_or_update(self, crypto_data: List[dict]) -> List[Cryptocurrency]:
        """Efficiently create or update multiple cryptocurrencies."""
        try:
            result = []
            existing_coins = {crypto.coin_id: crypto for crypto in 
                            self.get_by_coin_ids([data['coin_id'] for data in crypto_data])}
            
            for data in crypto_data:
                coin_id = data['coin_id']
                
                if coin_id in existing_coins:
                    # Update existing
                    crypto = existing_coins[coin_id]
                    for key, value in data.items():
                        if key != 'coin_id' and hasattr(crypto, key):
                            setattr(crypto, key, value)
                else:
                    # Create new
                    crypto = Cryptocurrency(**data)
                    self.session.add(crypto)
                
                result.append(crypto)
            
            self.session.flush()
            logger.debug(f"Bulk processed {len(result)} cryptocurrencies")
            return result
        except SQLAlchemyError as e:
            logger.error(f"Error in bulk create/update cryptocurrencies: {e}")
            raise
    
    def deactivate_cryptocurrency(self, coin_id: str) -> bool:
        """Mark cryptocurrency as inactive."""
        try:
            crypto = self.get_by_coin_id(coin_id)
            if crypto:
                crypto.is_active = False
                self.session.flush()
                logger.debug(f"Deactivated cryptocurrency {coin_id}")
                return True
            return False
        except SQLAlchemyError as e:
            logger.error(f"Error deactivating cryptocurrency {coin_id}: {e}")
            raise
    
    def search_by_name(self, name_pattern: str, limit: int = 10) -> List[Cryptocurrency]:
        """Search cryptocurrencies by name pattern."""
        try:
            return self.session.query(Cryptocurrency).filter(
                Cryptocurrency.name.ilike(f'%{name_pattern}%'),
                Cryptocurrency.is_active == True
            ).order_by(Cryptocurrency.market_cap_rank.asc().nulls_last()).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error searching cryptocurrencies by name {name_pattern}: {e}")
            raise