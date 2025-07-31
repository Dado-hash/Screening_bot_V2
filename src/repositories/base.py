"""Base repository with common database operations."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger

from src.database.models import Base

T = TypeVar('T', bound=Base)


class BaseRepository(Generic[T], ABC):
    """Base repository class with common CRUD operations."""
    
    def __init__(self, session: Session, model: Type[T]):
        self.session = session
        self.model = model
    
    def create(self, **kwargs) -> T:
        """Create a new record."""
        try:
            instance = self.model(**kwargs)
            self.session.add(instance)
            self.session.flush()
            logger.debug(f"Created {self.model.__name__} with id {instance.id}")
            return instance
        except SQLAlchemyError as e:
            logger.error(f"Error creating {self.model.__name__}: {e}")
            raise
    
    def get_by_id(self, id: int) -> Optional[T]:
        """Get record by ID."""
        try:
            return self.session.query(self.model).filter(self.model.id == id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting {self.model.__name__} by id {id}: {e}")
            raise
    
    def get_all(self, limit: Optional[int] = None, offset: int = 0) -> List[T]:
        """Get all records with optional pagination."""
        try:
            query = self.session.query(self.model)
            if offset > 0:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)
            return query.all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting all {self.model.__name__}: {e}")
            raise
    
    def update(self, id: int, **kwargs) -> Optional[T]:
        """Update record by ID."""
        try:
            instance = self.get_by_id(id)
            if instance:
                for key, value in kwargs.items():
                    if hasattr(instance, key):
                        setattr(instance, key, value)
                self.session.flush()
                logger.debug(f"Updated {self.model.__name__} with id {id}")
            return instance
        except SQLAlchemyError as e:
            logger.error(f"Error updating {self.model.__name__} with id {id}: {e}")
            raise
    
    def delete(self, id: int) -> bool:
        """Delete record by ID."""
        try:
            instance = self.get_by_id(id)
            if instance:
                self.session.delete(instance)
                self.session.flush()
                logger.debug(f"Deleted {self.model.__name__} with id {id}")
                return True
            return False
        except SQLAlchemyError as e:
            logger.error(f"Error deleting {self.model.__name__} with id {id}: {e}")
            raise
    
    def count(self) -> int:
        """Count total records."""
        try:
            return self.session.query(self.model).count()
        except SQLAlchemyError as e:
            logger.error(f"Error counting {self.model.__name__}: {e}")
            raise
    
    def bulk_create(self, records: List[Dict[str, Any]]) -> List[T]:
        """Create multiple records efficiently."""
        try:
            instances = [self.model(**record) for record in records]
            self.session.add_all(instances)
            self.session.flush()
            logger.debug(f"Bulk created {len(instances)} {self.model.__name__} records")
            return instances
        except SQLAlchemyError as e:
            logger.error(f"Error bulk creating {self.model.__name__}: {e}")
            raise
    
    def exists(self, **filters) -> bool:
        """Check if record exists with given filters."""
        try:
            query = self.session.query(self.model)
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)
            return query.first() is not None
        except SQLAlchemyError as e:
            logger.error(f"Error checking existence in {self.model.__name__}: {e}")
            raise