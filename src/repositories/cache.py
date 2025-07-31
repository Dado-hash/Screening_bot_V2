"""Repository for cache operations."""

import json
from datetime import datetime, timedelta
from typing import Optional, Any, Dict

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from loguru import logger

from .base import BaseRepository
from ..database.models import CacheEntry


class CacheRepository(BaseRepository[CacheEntry]):
    """Repository for cache operations."""
    
    def __init__(self, session: Session):
        super().__init__(session, CacheEntry)
    
    def get_cached_value(self, cache_key: str) -> Optional[Any]:
        """Get cached value by key, returns None if expired or not found."""
        try:
            entry = self.session.query(CacheEntry).filter(
                CacheEntry.cache_key == cache_key
            ).first()
            
            if entry is None:
                return None
                
            if entry.is_expired:
                # Remove expired entry
                self.session.delete(entry)
                self.session.flush()
                logger.debug(f"Removed expired cache entry: {cache_key}")
                return None
            
            # Deserialize and return cached value
            cached_value = json.loads(entry.cache_value)
            logger.debug(f"Cache hit for key: {cache_key}")
            return cached_value
            
        except (SQLAlchemyError, json.JSONDecodeError) as e:
            logger.error(f"Error getting cached value for key {cache_key}: {e}")
            return None
    
    def set_cached_value(self, cache_key: str, value: Any, ttl_seconds: int = 3600, 
                        cache_type: str = 'general') -> bool:
        """Set cached value with TTL."""
        try:
            # Remove existing entry if it exists
            existing = self.session.query(CacheEntry).filter(
                CacheEntry.cache_key == cache_key
            ).first()
            
            if existing:
                self.session.delete(existing)
            
            # Create new cache entry
            expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
            cache_value = json.dumps(value, default=str)  # Handle datetime serialization
            
            new_entry = CacheEntry(
                cache_key=cache_key,
                cache_value=cache_value,
                cache_type=cache_type,
                ttl_seconds=ttl_seconds,
                expires_at=expires_at
            )
            
            self.session.add(new_entry)
            self.session.flush()
            
            logger.debug(f"Cached value for key: {cache_key}, expires at: {expires_at}")
            return True
            
        except (SQLAlchemyError, json.JSONEncodeError) as e:
            logger.error(f"Error setting cached value for key {cache_key}: {e}")
            return False
    
    def invalidate_cache(self, cache_key: str) -> bool:
        """Remove specific cache entry."""
        try:
            entry = self.session.query(CacheEntry).filter(
                CacheEntry.cache_key == cache_key
            ).first()
            
            if entry:
                self.session.delete(entry)
                self.session.flush()
                logger.debug(f"Invalidated cache for key: {cache_key}")
                return True
            
            return False
            
        except SQLAlchemyError as e:
            logger.error(f"Error invalidating cache for key {cache_key}: {e}")
            return False
    
    def invalidate_cache_by_type(self, cache_type: str) -> int:
        """Remove all cache entries of a specific type."""
        try:
            deleted_count = self.session.query(CacheEntry).filter(
                CacheEntry.cache_type == cache_type
            ).delete()
            
            self.session.flush()
            logger.debug(f"Invalidated {deleted_count} cache entries of type: {cache_type}")
            return deleted_count
            
        except SQLAlchemyError as e:
            logger.error(f"Error invalidating cache by type {cache_type}: {e}")
            return 0
    
    def cleanup_expired_entries(self) -> int:
        """Remove all expired cache entries."""
        try:
            current_time = datetime.utcnow()
            deleted_count = self.session.query(CacheEntry).filter(
                CacheEntry.expires_at < current_time
            ).delete()
            
            self.session.flush()
            logger.debug(f"Cleaned up {deleted_count} expired cache entries")
            return deleted_count
            
        except SQLAlchemyError as e:
            logger.error(f"Error cleaning up expired cache entries: {e}")
            return 0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            current_time = datetime.utcnow()
            
            # Total entries
            total_entries = self.session.query(CacheEntry).count()
            
            # Active (non-expired) entries
            active_entries = self.session.query(CacheEntry).filter(
                CacheEntry.expires_at > current_time
            ).count()
            
            # Expired entries
            expired_entries = total_entries - active_entries
            
            # Entries by type
            type_stats = {}
            for cache_type, count in self.session.query(
                CacheEntry.cache_type,
                func.count(CacheEntry.id)
            ).group_by(CacheEntry.cache_type).all():
                type_stats[cache_type] = count
            
            return {
                'total_entries': total_entries,
                'active_entries': active_entries,
                'expired_entries': expired_entries,
                'entries_by_type': type_stats
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}
    
    def cache_exists(self, cache_key: str) -> bool:
        """Check if cache key exists and is not expired."""
        try:
            entry = self.session.query(CacheEntry).filter(
                CacheEntry.cache_key == cache_key
            ).first()
            
            if entry is None:
                return False
            
            if entry.is_expired:
                # Clean up expired entry
                self.session.delete(entry)
                self.session.flush()
                return False
            
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Error checking cache existence for key {cache_key}: {e}")
            return False
    
    def get_or_set(self, cache_key: str, fetch_function, ttl_seconds: int = 3600, 
                   cache_type: str = 'general') -> Any:
        """Get cached value or execute function and cache result."""
        # Try to get from cache first
        cached_value = self.get_cached_value(cache_key)
        
        if cached_value is not None:
            return cached_value
        
        # Execute function and cache result
        try:
            fresh_value = fetch_function()
            self.set_cached_value(cache_key, fresh_value, ttl_seconds, cache_type)
            logger.debug(f"Executed function and cached result for key: {cache_key}")
            return fresh_value
        except Exception as e:
            logger.error(f"Error executing fetch function for cache key {cache_key}: {e}")
            raise