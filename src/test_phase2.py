#!/usr/bin/env python3
"""
Test script for Phase 2 - Modern Screening Service

This script tests the modernized screening algorithms and services.
"""

import sys
import asyncio
from datetime import date, timedelta
from pathlib import Path

# Add the parent directory (root project) to path so we can import from src
sys.path.insert(0, str(Path(__file__).parent.parent))

# Also add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from loguru import logger
from colorama import init, Fore, Style

from src.services.screening_service import ScreeningService
from src.services.data_service import DataService
from src.services.coingecko_service import CoinGeckoService
from src.config.settings import get_config
from src.database.connection import check_database_connection

# Initialize colorama
init()


def print_banner():
    """Print test banner."""
    banner = f"""
{Fore.CYAN}
╔══════════════════════════════════════════════════════════════╗
║                    PHASE 2 TEST SUITE                       ║
║              Modern Screening Service Test                   ║
╚══════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}
"""
    print(banner)


def test_configuration_system():
    """Test 1: Configuration system."""
    print(f"\n{Fore.YELLOW}🔍 Test 1: Configuration System{Style.RESET_ALL}")
    
    try:
        config = get_config()
        
        print(f"✅ Configuration loaded successfully")
        print(f"  Database URL: {config.database.url}")
        print(f"  Default coins limit: {config.screening.default_coins_limit}")
        print(f"  SMA periods: {config.screening.sma_fast}, {config.screening.sma_medium}, {config.screening.sma_slow}")
        print(f"  Cache enabled: {config.cache.enabled}")
        
        return True
        
    except Exception as e:
        print(f"{Fore.RED}❌ Configuration test failed: {e}{Style.RESET_ALL}")
        return False


async def test_data_preparation():
    """Test 2: Prepare some test data."""
    print(f"\n{Fore.YELLOW}🔍 Test 2: Data Preparation{Style.RESET_ALL}")
    
    try:
        data_service = DataService()
        stats = data_service.get_data_coverage_stats()
        
        print(f"Current database state:")
        print(f"  Cryptocurrencies: {stats['total_cryptocurrencies']}")
        print(f"  Price records: {stats['total_price_records']}")
        
        # If no data, fetch a small sample
        if stats['total_cryptocurrencies'] == 0:
            print("No data found. Fetching sample data...")
            
            coingecko_service = CoinGeckoService()
            
            # Fetch top 5 cryptocurrencies with 7 days of data
            sync_stats = await coingecko_service.sync_all_data(5, 7)
            
            print(f"✅ Sample data fetched:")
            print(f"  Cryptocurrencies: {sync_stats['cryptocurrencies_synced']}")
            print(f"  Price records: {sync_stats['price_records_synced']}")
            print(f"  SMA records: {sync_stats['sma_records_synced']}")
        else:
            print(f"✅ Sufficient data available for testing")
        
        return True
        
    except Exception as e:
        print(f"{Fore.RED}❌ Data preparation failed: {e}{Style.RESET_ALL}")
        return False


def test_screening_service():
    """Test 3: Modern screening service."""
    print(f"\n{Fore.YELLOW}🔍 Test 3: Modern Screening Service{Style.RESET_ALL}")
    
    try:
        # Initialize services
        data_service = DataService()
        screening_service = ScreeningService()
        
        # Get available cryptocurrencies
        cryptos = data_service.get_active_cryptocurrencies(5)  # Test with 5 coins
        
        if not cryptos:
            print(f"{Fore.YELLOW}⚠️  No cryptocurrencies available for testing{Style.RESET_ALL}")
            return False
        
        coin_ids = [crypto['coin_id'] for crypto in cryptos]
        print(f"Testing with {len(coin_ids)} cryptocurrencies: {', '.join(coin_ids)}")
        
        # Run screening analysis
        analysis_date = date.today() - timedelta(days=1)  # Yesterday
        timeframes = [1, 3, 7]  # Test with short timeframes
        
        print(f"Running screening analysis for {analysis_date}...")
        
        results = screening_service.run_comprehensive_screening(
            coin_ids=coin_ids,
            analysis_date=analysis_date,
            direction='backward',
            timeframes=timeframes
        )
        
        # Validate results
        if results and 'leaderboard' in results:
            leaderboard = results['leaderboard']
            statistics = results.get('statistics', {})
            
            print(f"✅ Screening completed successfully:")
            print(f"  Total coins analyzed: {len(leaderboard)}")
            print(f"  Analysis date: {results.get('analysis_date')}")
            print(f"  Direction: {results.get('direction')}")
            print(f"  Timeframes: {results.get('timeframes')}")
            
            if statistics:
                print(f"  Total analyses: {statistics.get('total_analyses', 0)}")
                if 'score_stats' in statistics:
                    score_stats = statistics['score_stats']
                    print(f"  Score range: {score_stats['min']:.1f} to {score_stats['max']:.1f}")
            
            # Show top 3 results
            print(f"\n  Top 3 results:")
            for i, coin_data in enumerate(leaderboard[:3]):
                coin_id = coin_data['coin_id'].upper()
                total_score = coin_data['total_score']
                avg_return = coin_data['avg_return']
                print(f"    {i+1}. {coin_id}: Score {total_score:.1f}, Avg Return {avg_return:.2f}%")
            
            return True
        else:
            print(f"{Fore.YELLOW}⚠️  No results returned from screening{Style.RESET_ALL}")
            return False
        
    except Exception as e:
        print(f"{Fore.RED}❌ Screening service test failed: {e}{Style.RESET_ALL}")
        logger.error(f"Screening service error: {e}")
        return False


def test_export_functionality():
    """Test 4: Export functionality."""
    print(f"\n{Fore.YELLOW}🔍 Test 4: Export Functionality{Style.RESET_ALL}")
    
    try:
        # Run a quick screening to get results
        data_service = DataService()
        screening_service = ScreeningService()
        
        cryptos = data_service.get_active_cryptocurrencies(3)
        if not cryptos:
            print(f"{Fore.YELLOW}⚠️  No data for export test{Style.RESET_ALL}")
            return False
        
        coin_ids = [crypto['coin_id'] for crypto in cryptos]
        
        results = screening_service.run_comprehensive_screening(
            coin_ids=coin_ids,
            analysis_date=date.today() - timedelta(days=1),
            direction='backward',
            timeframes=[1, 3]
        )
        
        if results:
            # Test export
            output_path = "data/outputs/test_screening_results.xlsx"
            success = screening_service.export_results_to_excel(results, output_path)
            
            if success:
                print(f"✅ Results exported successfully to {output_path}")
                
                # Check if file exists
                from pathlib import Path
                if Path(output_path).exists():
                    print(f"✅ Export file verified")
                    return True
                else:
                    print(f"{Fore.RED}❌ Export file not found{Style.RESET_ALL}")
                    return False
            else:
                print(f"{Fore.RED}❌ Export failed{Style.RESET_ALL}")
                return False
        else:
            print(f"{Fore.YELLOW}⚠️  No results to export{Style.RESET_ALL}")
            return False
        
    except Exception as e:
        print(f"{Fore.RED}❌ Export test failed: {e}{Style.RESET_ALL}")
        return False


def test_performance_comparison():
    """Test 5: Performance comparison with old system."""
    print(f"\n{Fore.YELLOW}🔍 Test 5: Performance Comparison{Style.RESET_ALL}")
    
    try:
        import time
        
        data_service = DataService()
        screening_service = ScreeningService()
        
        cryptos = data_service.get_active_cryptocurrencies(10)
        if len(cryptos) < 5:
            print(f"{Fore.YELLOW}⚠️  Insufficient data for performance test{Style.RESET_ALL}")
            return False
        
        coin_ids = [crypto['coin_id'] for crypto in cryptos]
        
        # Time the modern screening
        start_time = time.time()
        
        results = screening_service.run_comprehensive_screening(
            coin_ids=coin_ids,
            analysis_date=date.today() - timedelta(days=1),
            direction='backward',
            timeframes=[1, 3, 7, 14]
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        if results:
            leaderboard = results['leaderboard']
            total_analyses = results.get('statistics', {}).get('total_analyses', 0)
            
            print(f"✅ Performance test completed:")
            print(f"  Coins analyzed: {len(coin_ids)}")
            print(f"  Timeframes: 4")
            print(f"  Total analyses: {total_analyses}")
            print(f"  Execution time: {execution_time:.2f} seconds")
            print(f"  Analyses per second: {total_analyses/execution_time:.1f}")
            
            return True
        else:
            print(f"{Fore.RED}❌ Performance test failed - no results{Style.RESET_ALL}")
            return False
        
    except Exception as e:
        print(f"{Fore.RED}❌ Performance test failed: {e}{Style.RESET_ALL}")
        return False


async def main():
    """Run all Phase 2 tests."""
    print_banner()
    
    print(f"{Fore.BLUE}Starting Phase 2 comprehensive test...{Style.RESET_ALL}")
    
    # Check database connection
    if not check_database_connection():
        print(f"{Fore.RED}❌ Database connection failed{Style.RESET_ALL}")
        return
    
    test_results = []
    
    # Run all tests
    test_results.append(("Configuration System", test_configuration_system()))
    test_results.append(("Data Preparation", await test_data_preparation()))
    test_results.append(("Screening Service", test_screening_service()))
    test_results.append(("Export Functionality", test_export_functionality()))
    test_results.append(("Performance Comparison", test_performance_comparison()))
    
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
        print(f"\n{Fore.GREEN}🎉 All Phase 2 tests passed! The modern screening system is working perfectly!{Style.RESET_ALL}")
        print(f"\n🚀 Ready for Phase 3: Web Dashboard Implementation")
    else:
        print(f"\n{Fore.YELLOW}⚠️  Some tests failed. Check the details above.{Style.RESET_ALL}")


if __name__ == "__main__":
    asyncio.run(main())