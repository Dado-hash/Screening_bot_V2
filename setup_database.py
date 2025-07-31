#!/usr/bin/env python3
"""
Database setup script for Screening Bot V2.

This script initializes the database and performs initial setup.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from loguru import logger
from src.database.migrations import DatabaseMigrator


def main():
    """Main setup function."""
    logger.info("🚀 Starting Screening Bot V2 database setup")
    
    # Create data directory if it doesn't exist
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Initialize database
    migrator = DatabaseMigrator()
    
    print("Initializing database...")
    if migrator.initialize_database():
        print("✅ Database initialized successfully")
        
        # Run health check
        print("\nRunning health check...")
        health = migrator.check_database_health()
        
        if health['connected'] and health['tables_exist']:
            print("✅ Database health check passed")
            print(f"📊 Tables created: {list(health['table_counts'].keys())}")
        else:
            print("❌ Database health check failed")
            for error in health.get('errors', []):
                print(f"   Error: {error}")
            return False
    else:
        print("❌ Database initialization failed")
        return False
    
    print("\n🎉 Database setup completed successfully!")
    print("\nNext steps:")
    print("1. Configure your API keys in config/api_keys.py")
    print("2. Run: python main.py")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)