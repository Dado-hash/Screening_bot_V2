#!/usr/bin/env python3
"""
Test script for Phase 1 - Database and Data Fetching

This script tests the new database system and data fetching capabilities.
"""

import sys
import asyncio
from pathlib import Path
import os

from loguru import logger
from colorama import init, Fore, Style

# Import our services using relative imports now that we're in src
from database.connection import DatabaseTransaction, check_database_connection
from database.migrations import DatabaseMigrator
from services.coingecko_service import CoinGeckoService
from services.data_service import DataService

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
    
    if check_database_connection():
        print(f"{Fore.GREEN}✅ Database connection successful{Style.RESET_ALL}")
        
        # Test health check
        migrator = DatabaseMigrator()
        health = migrator.check_database_health()
        
        print(f"Connected: {'✅' if health['connected'] else '❌'}")
        print(f"Tables exist: {'✅' if health['tables_exist'] else '❌'}")
        print(f"Can write: {'✅' if health['can_write'] else '❌'}")
        
        if health['table_counts']:
            print("Table counts:")
            for table, count in health['table_counts'].items():
                print(f"  {table}: {count:,} records")
        
        return True
    else:
        print(f"{Fore.RED}❌ Database connection failed{Style.RESET_ALL}")
        return False


async def test_small_data_fetch():
    """Test 2: Small data fetch (top 5 cryptocurrencies)."""
    print(f"\n{Fore.YELLOW}🔍 Test 2: Small Data Fetch (Top 5 Cryptos){Style.RESET_ALL}")
    
    try:
        # Initialize CoinGecko service
        coingecko_service = CoinGeckoService()
        
        print("Fetching top 5 cryptocurrencies...")
        crypto_data = await coingecko_service.fetch_top_cryptocurrencies(limit=5)
        
        print(f"✅ Fetched {len(crypto_data)} cryptocurrencies:")
        for crypto in crypto_data:
            print(f"  {crypto['symbol'].upper()}: {crypto['name']} (Rank: {crypto.get('market_cap_rank', 'N/A')})")
        
        # Store to database
        stored_count = await coingecko_service.store_cryptocurrencies_to_db(crypto_data)
        print(f"✅ Stored {stored_count} cryptocurrencies to database")
        
        return True
        
    except Exception as e:
        print(f"{Fore.RED}❌ Data fetch failed: {e}{Style.RESET_ALL}")
        logger.error(f"Data fetch error: {e}")
        return False


async def test_historical_data_fetch():
    """Test 3: Historical data fetch for Bitcoin."""
    print(f"\n{Fore.YELLOW}🔍 Test 3: Historical Data Fetch (Bitcoin, 7 days){Style.RESET_ALL}")
    
    try:
        coingecko_service = CoinGeckoService()
        
        print("Fetching Bitcoin historical data (7 days)...")
        historical_data = await coingecko_service.fetch_historical_data('bitcoin', 'btc', 7)
        
        print(f"✅ Fetched {len(historical_data)} historical data points")
        if historical_data:
            latest = historical_data[-1]
            print(f"  Latest: {latest['date']} - Price: {latest['price']:.8f} BTC")
        
        # Store to database
        stored_count = await coingecko_service.store_historical_data_to_db('bitcoin', historical_data, 'btc')
        print(f"✅ Stored {stored_count} price records to database")
        
        return True
        
    except Exception as e:
        print(f"{Fore.RED}❌ Historical data fetch failed: {e}{Style.RESET_ALL}")
        logger.error(f"Historical data fetch error: {e}")
        return False


async def test_sma_calculation():
    """Test 4: SMA calculation for Bitcoin."""
    print(f"\n{Fore.YELLOW}🔍 Test 4: SMA Calculation (Bitcoin){Style.RESET_ALL}")
    
    try:
        coingecko_service = CoinGeckoService()
        
        print("Calculating SMA indicators for Bitcoin...")
        sma_count = await coingecko_service.calculate_and_store_sma('bitcoin', 30)
        
        print(f"✅ Calculated and stored {sma_count} SMA records")
        
        return True
        
    except Exception as e:
        print(f"{Fore.RED}❌ SMA calculation failed: {e}{Style.RESET_ALL}")
        logger.error(f"SMA calculation error: {e}")
        return False


def test_data_service():
    """Test 5: Data service operations."""
    print(f"\n{Fore.YELLOW}🔍 Test 5: Data Service Operations{Style.RESET_ALL}")
    
    try:
        data_service = DataService()
        
        # Test getting cryptocurrencies
        cryptos = data_service.get_active_cryptocurrencies(limit=5)
        print(f"✅ Retrieved {len(cryptos)} active cryptocurrencies from database")
        
        # Test statistics
        stats = data_service.get_data_coverage_stats()
        print(f"✅ Data coverage stats:")
        print(f"  Total cryptocurrencies: {stats['total_cryptocurrencies']}")
        print(f"  Total price records: {stats['total_price_records']}")
        print(f"  Total SMA records: {stats['total_sma_records']}")
        
        return True
        
    except Exception as e:
        print(f"{Fore.RED}❌ Data service test failed: {e}{Style.RESET_ALL}")
        logger.error(f"Data service error: {e}")
        return False


def test_cache_system():
    """Test 6: Cache system."""
    print(f"\n{Fore.YELLOW}🔍 Test 6: Cache System{Style.RESET_ALL}")
    
    try:
        from repositories.cache import CacheRepository
        
        with DatabaseTransaction() as session:
            cache_repo = CacheRepository(session)
            
            # Test setting cache
            test_key = "test_cache_key"
            test_value = {"message": "Hello Cache!", "timestamp": "2024-01-01"}
            
            success = cache_repo.set_cached_value(test_key, test_value, 60)
            print(f"✅ Cache set: {success}")
            
            # Test getting cache
            cached_value = cache_repo.get_cached_value(test_key)
            print(f"✅ Cache retrieved: {cached_value is not None}")
            
            if cached_value:
                print(f"  Cached message: {cached_value.get('message')}")
            
            # Test cache stats
            stats = cache_repo.get_cache_stats()
            print(f"✅ Cache stats: {stats['total_entries']} total entries")
            
        return True
        
    except Exception as e:
        print(f"{Fore.RED}❌ Cache system test failed: {e}{Style.RESET_ALL}")
        logger.error(f"Cache system error: {e}")
        return False


async def main():
    """Run all Phase 1 tests."""
    print_banner()
    
    print(f"{Fore.BLUE}Starting Phase 1 comprehensive test...{Style.RESET_ALL}")
    
    test_results = []
    
    # Run all tests
    test_results.append(("Database Connection", test_database_connection()))
    test_results.append(("Small Data Fetch", await test_small_data_fetch()))
    test_results.append(("Historical Data Fetch", await test_historical_data_fetch()))
    test_results.append(("SMA Calculation", await test_sma_calculation()))
    test_results.append(("Data Service", test_data_service()))
    test_results.append(("Cache System", test_cache_system()))
    
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
        print(f"\n{Fore.GREEN}🎉 All tests passed! Phase 1 is working perfectly!{Style.RESET_ALL}")
        
        # Show final database stats
        data_service = DataService()
        stats = data_service.get_data_coverage_stats()
        print(f"\n📊 Final Database State:")
        print(f"  Cryptocurrencies: {stats['total_cryptocurrencies']}")
        print(f"  Price records: {stats['total_price_records']}")
        print(f"  SMA records: {stats['total_sma_records']}")
        
    else:
        print(f"\n{Fore.YELLOW}⚠️  Some tests failed. Check logs for details.{Style.RESET_ALL}")


if __name__ == "__main__":
    asyncio.run(main())