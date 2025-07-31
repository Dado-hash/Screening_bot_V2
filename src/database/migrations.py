"""Database migration utilities."""

import os
from pathlib import Path
from typing import Dict, Any

from sqlalchemy import text
from loguru import logger

from .connection import get_engine, get_session_factory
from .models import Base


class DatabaseMigrator:
    """Simple database migration system."""
    
    def __init__(self):
        self.engine = get_engine()
        self.session_factory = get_session_factory()
    
    def initialize_database(self, drop_existing: bool = False) -> bool:
        """Initialize database with all tables."""
        try:
            if drop_existing:
                logger.warning("Dropping all existing tables")
                Base.metadata.drop_all(self.engine)
            
            logger.info("Creating database tables")
            Base.metadata.create_all(self.engine)
            
            # Create indexes if they don't exist
            self._create_custom_indexes()
            
            logger.info("Database initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            return False
    
    def _create_custom_indexes(self):
        """Create custom indexes for performance."""
        indexes = [
            # Performance indexes for common queries
            "CREATE INDEX IF NOT EXISTS idx_historical_prices_crypto_date_btc ON historical_prices(cryptocurrency_id, date, price_btc)",
            "CREATE INDEX IF NOT EXISTS idx_sma_indicators_crypto_date_all ON sma_indicators(cryptocurrency_id, date, above_sma_6, above_sma_11, above_sma_21)",
            "CREATE INDEX IF NOT EXISTS idx_screening_results_score_date ON screening_results(total_score DESC, analysis_date)",
            "CREATE INDEX IF NOT EXISTS idx_cache_entries_type_expires ON cache_entries(cache_type, expires_at)"
        ]
        
        with self.engine.connect() as conn:
            for index_sql in indexes:
                try:
                    conn.execute(text(index_sql))
                    logger.debug(f"Created index: {index_sql.split()[5]}")  # Extract index name
                except Exception as e:
                    logger.warning(f"Could not create index: {e}")
            conn.commit()
    
    def check_database_health(self) -> Dict[str, Any]:
        """Check database health and return status."""
        health_status = {
            'connected': False,
            'tables_exist': False,
            'can_write': False,
            'table_counts': {},
            'errors': []
        }
        
        try:
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                health_status['connected'] = True
            
            # Check if tables exist
            from sqlalchemy import inspect
            inspector = inspect(self.engine)
            existing_tables = inspector.get_table_names()
            expected_tables = [
                'cryptocurrencies', 
                'historical_prices', 
                'sma_indicators', 
                'screening_results',
                'cache_entries'
            ]
            
            health_status['tables_exist'] = all(table in existing_tables for table in expected_tables)
            
            # Get table counts
            if health_status['tables_exist']:
                session = self.session_factory()
                try:
                    for table in expected_tables:
                        count_query = text(f"SELECT COUNT(*) FROM {table}")
                        result = session.execute(count_query)
                        health_status['table_counts'][table] = result.scalar()
                    
                    # Test write capability
                    session.execute(text("CREATE TEMPORARY TABLE test_write (id INTEGER)"))
                    session.execute(text("DROP TABLE test_write"))
                    health_status['can_write'] = True
                    
                except Exception as e:
                    health_status['errors'].append(f"Database operation error: {e}")
                finally:
                    session.close()
        
        except Exception as e:
            health_status['errors'].append(f"Connection error: {e}")
        
        return health_status
    
    def backup_database(self, backup_path: str) -> bool:
        """Create a backup of the database (SQLite only)."""
        try:
            if not self.engine.url.database.endswith('.db'):
                logger.error("Backup only supported for SQLite databases")
                return False
            
            import shutil
            db_path = self.engine.url.database
            
            # Ensure backup directory exists
            backup_dir = Path(backup_path).parent
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(db_path, backup_path)
            logger.info(f"Database backed up to: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Database backup failed: {e}")
            return False
    
    def restore_database(self, backup_path: str) -> bool:
        """Restore database from backup (SQLite only)."""
        try:
            if not os.path.exists(backup_path):
                logger.error(f"Backup file not found: {backup_path}")
                return False
            
            if not self.engine.url.database.endswith('.db'):
                logger.error("Restore only supported for SQLite databases")
                return False
            
            import shutil
            db_path = self.engine.url.database
            
            # Close all connections
            self.engine.dispose()
            
            shutil.copy2(backup_path, db_path)
            logger.info(f"Database restored from: {backup_path}")
            
            # Reinitialize engine
            from .connection import _engine, _SessionFactory
            global _engine, _SessionFactory
            _engine = None
            _SessionFactory = None
            self.engine = get_engine()
            self.session_factory = get_session_factory()
            
            return True
            
        except Exception as e:
            logger.error(f"Database restore failed: {e}")
            return False
    
    def vacuum_database(self) -> bool:
        """Optimize database (SQLite VACUUM)."""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("VACUUM"))
                conn.commit()
            logger.info("Database vacuum completed")
            return True
            
        except Exception as e:
            logger.error(f"Database vacuum failed: {e}")
            return False


def init_database_cli(drop_existing: bool = False) -> None:
    """CLI function to initialize database."""
    migrator = DatabaseMigrator()
    
    if migrator.initialize_database(drop_existing):
        logger.info("✅ Database initialization successful")
        
        # Show health status
        health = migrator.check_database_health()
        logger.info(f"Database health check: {health}")
    else:
        logger.error("❌ Database initialization failed")


def check_database_cli() -> None:
    """CLI function to check database health."""
    migrator = DatabaseMigrator()
    health = migrator.check_database_health()
    
    print("\n📊 Database Health Report")
    print("=" * 40)
    print(f"Connected: {'✅' if health['connected'] else '❌'}")
    print(f"Tables exist: {'✅' if health['tables_exist'] else '❌'}")
    print(f"Can write: {'✅' if health['can_write'] else '❌'}")
    
    if health['table_counts']:
        print("\n📋 Table Counts:")
        for table, count in health['table_counts'].items():
            print(f"  {table}: {count:,} records")
    
    if health['errors']:
        print(f"\n❌ Errors:")
        for error in health['errors']:
            print(f"  - {error}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "init":
            drop = "--drop" in sys.argv
            init_database_cli(drop_existing=drop)
        elif command == "check":
            check_database_cli()
        elif command == "vacuum":
            migrator = DatabaseMigrator()
            migrator.vacuum_database()
        else:
            print("Usage: python migrations.py [init|check|vacuum] [--drop]")
    else:
        print("Usage: python migrations.py [init|check|vacuum] [--drop]")