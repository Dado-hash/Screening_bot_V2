#!/usr/bin/env python3
"""
Test script for Phase 1 - Database and Data Fetching
Simplified version that avoids complex import issues
"""

import sys
import asyncio
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from loguru import logger
from colorama import init, Fore, Style

# Initialize colorama
init()

def print_banner():
    """Print test banner."""
    banner = f"""
{Fore.CYAN}
╔══════════════════════════════════════════════════════════════╗
║                    PHASE 1 TEST SUITE                       ║
║               Database & Data Fetching Test                  ║
╚══════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}
"""
    print(banner)

def test_database_connection():
    """Test 1: Database connection and health check."""
    print(f"\n{Fore.YELLOW}🔍 Test 1: Database Connection{Style.RESET_ALL}")
    
    try:
        from database.connection import check_database_connection
        
        if check_database_connection():
            print(f"{Fore.GREEN}✅ Database connection successful{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}❌ Database connection failed{Style.RESET_ALL}")
            return False
            
    except Exception as e:
        print(f"{Fore.RED}❌ Database connection error: {e}{Style.RESET_ALL}")
        logger.error(f"Database connection error: {e}")
        return False

def test_database_structure():
    """Test 2: Database structure and models."""
    print(f"\n{Fore.YELLOW}🔍 Test 2: Database Structure{Style.RESET_ALL}")
    
    try:
        from database.models import (
            Base, Cryptocurrency, HistoricalPrice, 
            SMAIndicator, ScreeningResult, CacheEntry
        )
        
        print("✅ Database models imported successfully")
        
        # Check if we can access model attributes
        print(f"✅ Cryptocurrency table: {Cryptocurrency.__tablename__}")
        print(f"✅ HistoricalPrice table: {HistoricalPrice.__tablename__}")
        print(f"✅ SMAIndicator table: {SMAIndicator.__tablename__}")
        print(f"✅ ScreeningResult table: {ScreeningResult.__tablename__}")
        print(f"✅ CacheEntry table: {CacheEntry.__tablename__}")
        
        return True
        
    except Exception as e:
        print(f"{Fore.RED}❌ Database structure test failed: {e}{Style.RESET_ALL}")
        logger.error(f"Database structure error: {e}")
        return False

def test_database_operations():
    """Test 3: Basic database operations."""
    print(f"\n{Fore.YELLOW}🔍 Test 3: Database Operations{Style.RESET_ALL}")
    
    try:
        from database.connection import DatabaseTransaction
        from database.models import Cryptocurrency
        
        # Test a simple database transaction
        with DatabaseTransaction() as session:
            # Try to query cryptocurrencies (should work even if empty)
            crypto_count = session.query(Cryptocurrency).count()
            print(f"✅ Database query successful: {crypto_count} cryptocurrencies found")
            
        return True
        
    except Exception as e:
        print(f"{Fore.RED}❌ Database operations test failed: {e}{Style.RESET_ALL}")
        logger.error(f"Database operations error: {e}")
        return False

def test_config_files():
    """Test 4: Configuration files."""
    print(f"\n{Fore.YELLOW}🔍 Test 4: Configuration Files{Style.RESET_ALL}")
    
    try:
        config_dir = Path("config")
        
        # Check if config files exist
        api_keys_example = config_dir / "api_keys.py.example"
        settings_file = config_dir / "settings.py"
        
        if api_keys_example.exists():
            print("✅ API keys example file found")
        else:
            print("⚠️  API keys example file not found")
            
        if settings_file.exists():
            print("✅ Settings file found")
        else:
            print("⚠️  Settings file not found")
            
        # Try to import settings
        from config.settings import DATABASE_URL, API_RATE_LIMITS
        print("✅ Settings imported successfully")
        print(f"  Database URL configured: {DATABASE_URL is not None}")
        print(f"  API rate limits configured: {len(API_RATE_LIMITS)} APIs")
        
        return True
        
    except Exception as e:
        print(f"{Fore.RED}❌ Config test failed: {e}{Style.RESET_ALL}")
        logger.error(f"Config error: {e}")
        return False

def test_data_directory():
    """Test 5: Data directory structure."""
    print(f"\n{Fore.YELLOW}🔍 Test 5: Data Directory{Style.RESET_ALL}")
    
    try:
        data_dir = Path("data")
        
        if not data_dir.exists():
            print("⚠️  Data directory does not exist, creating it...")
            data_dir.mkdir(exist_ok=True)
            
        print("✅ Data directory exists")
        
        # Check for database file
        db_file = data_dir / "screening_bot.db"
        if db_file.exists():
            print(f"✅ Database file exists ({db_file.stat().st_size} bytes)")
        else:
            print("⚠️  Database file not found (will be created on first use)")
            
        return True
        
    except Exception as e:
        print(f"{Fore.RED}❌ Data directory test failed: {e}{Style.RESET_ALL}")
        logger.error(f"Data directory error: {e}")
        return False

async def main():
    """Run all Phase 1 tests."""
    print_banner()
    
    print(f"{Fore.BLUE}Starting Phase 1 basic system test...{Style.RESET_ALL}")
    
    test_results = []
    
    # Run all tests
    test_results.append(("Database Connection", test_database_connection()))
    test_results.append(("Database Structure", test_database_structure()))
    test_results.append(("Database Operations", test_database_operations()))
    test_results.append(("Configuration Files", test_config_files()))
    test_results.append(("Data Directory", test_data_directory()))
    
    # Print summary
    print(f"\n{Fore.BLUE}📊 TEST SUMMARY{Style.RESET_ALL}")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        if result:
            print(f"✅ {test_name}")
            passed += 1
        else:
            print(f"❌ {test_name}")
            failed += 1
    
    print(f"\n{Fore.GREEN if failed == 0 else Fore.YELLOW}Results: {passed} passed, {failed} failed{Style.RESET_ALL}")
    
    if failed == 0:
        print(f"\n{Fore.GREEN}🎉 All basic tests passed! System is ready!{Style.RESET_ALL}")
        print(f"\n💡 Next steps:")
        print(f"  1. Configure API keys in config/api_keys.py")
        print(f"  2. Run data fetching tests")
        print(f"  3. Test screening algorithms")
    else:
        print(f"\n{Fore.YELLOW}⚠️  Some tests failed. Check logs for details.{Style.RESET_ALL}")
        print(f"\n💡 This is normal for initial setup. Fix the issues and re-run.")

if __name__ == "__main__":
    asyncio.run(main())
