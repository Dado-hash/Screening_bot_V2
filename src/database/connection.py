"""Database connection and session management."""

import os
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine, Engine, text
from sqlalchemy.orm import sessionmaker, Session
from loguru import logger

from .models import Base

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/screening_bot.db')
DATABASE_ECHO = os.getenv('DATABASE_ECHO', 'false').lower() == 'true'

# Global engine and session factory
_engine: Engine = None
_SessionFactory: sessionmaker = None


def get_engine() -> Engine:
    """Get or create the database engine."""
    global _engine
    
    if _engine is None:
        # Ensure data directory exists for SQLite
        if DATABASE_URL.startswith('sqlite:///'):
            db_path = DATABASE_URL.replace('sqlite:///', '')
            db_dir = Path(db_path).parent
            db_dir.mkdir(parents=True, exist_ok=True)
        
        _engine = create_engine(
            DATABASE_URL,
            echo=DATABASE_ECHO,
            pool_pre_ping=True,
            # SQLite specific optimizations
            connect_args={'check_same_thread': False} if DATABASE_URL.startswith('sqlite') else {}
        )
        
        logger.info(f"Database engine created with URL: {DATABASE_URL}")
    
    return _engine


def get_session_factory() -> sessionmaker:
    """Get or create the session factory."""
    global _SessionFactory
    
    if _SessionFactory is None:
        engine = get_engine()
        _SessionFactory = sessionmaker(bind=engine, expire_on_commit=False)
        logger.debug("Session factory created")
    
    return _SessionFactory


def get_session() -> Generator[Session, None, None]:
    """Get a database session (context manager)."""
    SessionFactory = get_session_factory()
    session = SessionFactory()
    
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        session.close()


def init_database(drop_all: bool = False) -> None:
    """Initialize the database by creating all tables."""
    engine = get_engine()
    
    if drop_all:
        logger.warning("Dropping all database tables")
        Base.metadata.drop_all(engine)
    
    logger.info("Creating database tables")
    Base.metadata.create_all(engine)
    logger.info("Database initialization complete")


def check_database_connection() -> bool:
    """Check if database connection is working."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


# Context manager for transactions
class DatabaseTransaction:
    """Context manager for database transactions."""
    
    def __init__(self):
        self.session = None
    
    def __enter__(self) -> Session:
        SessionFactory = get_session_factory()
        self.session = SessionFactory()
        return self.session
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.session.rollback()
            logger.error(f"Transaction rolled back due to error: {exc_val}")
        else:
            self.session.commit()
        
        self.session.close()
        return False  # Don't suppress exceptions