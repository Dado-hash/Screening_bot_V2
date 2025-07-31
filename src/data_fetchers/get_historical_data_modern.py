#!/usr/bin/env python3
"""
Modern historical data fetcher using database and async operations.

This replaces the original get_historical_data_coingecko.py with a more robust implementation.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import questionary
from loguru import logger
from colorama import init, Fore, Style

from services.coingecko_service import CoinGeckoService
from services.data_service import DataService
from database.connection import check_database_connection, init_database

# Initialize colorama
init()


def print_banner():
    """Print application banner."""
    banner = f"""
{Fore.CYAN}
╔══════════════════════════════════════════════════════════════╗
║                 MODERN DATA FETCHER V2                       ║
║                 Database-Powered & Async                     ║
╚══════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}
"""
    print(banner)


async def fetch_data_interactive():
    """Interactive data fetching with user prompts."""
    print(f"\n{Fore.GREEN}🔄 Starting interactive data fetch...{Style.RESET_ALL}")
    
    # Get user preferences
    coin_limit = questionary.text(
        "How many top cryptocurrencies to fetch?", 
        default="100"
    ).ask()
    
    days = questionary.text(
        "How many days of historical data?", 
        default="365"
    ).ask()
    
    api_key = questionary.text(
        "CoinGecko API key (optional, press Enter to skip):",
        default=""
    ).ask()
    
    try:
        coin_limit = int(coin_limit)
        days = int(days)
        api_key = api_key.strip() or None
        
        if coin_limit <= 0 or days <= 0:
            raise ValueError("Values must be positive")
            
    except ValueError as e:
        print(f"{Fore.RED}❌ Invalid input: {e}{Style.RESET_ALL}")
        return False
    
    # Initialize services
    coingecko_service = CoinGeckoService(api_key=api_key)
    
    print(f"\n{Fore.YELLOW}📊 Configuration:{Style.RESET_ALL}")
    print(f"  • Cryptocurrencies: {coin_limit}")
    print(f"  • Historical days: {days}")
    print(f"  • API key: {'✅ Provided' if api_key else '❌ Using free tier'}")
    
    confirm = questionary.confirm(
        "Proceed with data fetching? This may take several minutes."
    ).ask()
    
    if not confirm:
        print(f"{Fore.YELLOW}Operation cancelled.{Style.RESET_ALL}")
        return False
    
    # Start fetching
    try:
        print(f"\n{Fore.GREEN}🚀 Starting data synchronization...{Style.RESET_ALL}")
        
        stats = await coingecko_service.sync_all_data(coin_limit, days)
        
        print(f"\n{Fore.GREEN}✅ Data sync completed successfully!{Style.RESET_ALL}")
        print(f"\n📊 Statistics:")
        print(f"  • Cryptocurrencies synced: {stats['cryptocurrencies_synced']}")
        print(f"  • Price records synced: {stats['price_records_synced']:,}")
        print(f"  • SMA records synced: {stats['sma_records_synced']:,}")
        
        if stats['errors'] > 0:
            print(f"  • Errors encountered: {stats['errors']}")
        
        return True
        
    except Exception as e:
        print(f"\n{Fore.RED}❌ Error during data sync: {e}{Style.RESET_ALL}")
        logger.error(f"Data sync failed: {e}")
        return False


async def quick_update():
    """Quick update for existing data."""
    print(f"\n{Fore.GREEN}⚡ Starting quick update...{Style.RESET_ALL}")
    
    data_service = DataService()
    
    # Get existing cryptocurrencies
    existing_cryptos = data_service.get_active_cryptocurrencies()
    
    if not existing_cryptos:
        print(f"{Fore.YELLOW}⚠️ No cryptocurrencies found in database. Run full sync first.{Style.RESET_ALL}")
        return False
    
    print(f"Found {len(existing_cryptos)} cryptocurrencies in database")
    
    # Update last 7 days for all existing cryptos
    coingecko_service = CoinGeckoService()
    coin_ids = [crypto['coin_id'] for crypto in existing_cryptos[:50]]  # Limit for quick update
    
    try:
        stats = await coingecko_service.sync_all_data(len(coin_ids), 7)
        
        print(f"\n{Fore.GREEN}✅ Quick update completed!{Style.RESET_ALL}")
        print(f"  • Updated {stats['cryptocurrencies_synced']} cryptocurrencies")
        print(f"  • Added {stats['price_records_synced']:,} price records")
        
        return True
        
    except Exception as e:
        print(f"\n{Fore.RED}❌ Quick update failed: {e}{Style.RESET_ALL}")
        return False


def show_data_stats():
    """Show current data statistics."""
    print(f"\n{Fore.BLUE}📊 Database Statistics{Style.RESET_ALL}")
    print("=" * 50)
    
    try:
        data_service = DataService()
        stats = data_service.get_data_coverage_stats()
        
        print(f"Total cryptocurrencies: {stats['total_cryptocurrencies']:,}")
        print(f"Active cryptocurrencies: {stats['active_cryptocurrencies']:,}")
        print(f"Total price records: {stats['total_price_records']:,}")
        print(f"Total SMA records: {stats['total_sma_records']:,}")
        
        if stats['latest_prices']:
            print(f"\nLatest prices (sample):")
            for price in stats['latest_prices'][:5]:
                print(f"  {price['coin_id']}: {price['price_btc']:.8f} BTC ({price['date']})")
        
    except Exception as e:
        print(f"{Fore.RED}❌ Error getting statistics: {e}{Style.RESET_ALL}")


def export_to_excel():
    """Export data to Excel for compatibility with old system."""
    print(f"\n{Fore.BLUE}📤 Exporting data to Excel...{Style.RESET_ALL}")
    
    try:
        data_service = DataService()
        
        # Get top cryptocurrencies
        cryptos = data_service.get_active_cryptocurrencies(100)
        coin_ids = [crypto['coin_id'] for crypto in cryptos]
        
        if not coin_ids:
            print(f"{Fore.YELLOW}⚠️ No cryptocurrencies found in database{Style.RESET_ALL}")
            return False
        
        # Export data
        success = data_service.export_data_to_excel(coin_ids, 30)
        
        if success:
            print(f"{Fore.GREEN}✅ Data exported to data/outputs/exported_data.xlsx{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ Export failed{Style.RESET_ALL}")
        
        return success
        
    except Exception as e:
        print(f"{Fore.RED}❌ Export error: {e}{Style.RESET_ALL}")
        return False


async def main():
    """Main function."""
    print_banner()
    
    # Check database connection
    if not check_database_connection():
        print(f"{Fore.RED}❌ Database connection failed{Style.RESET_ALL}")
        print("Run: python setup_database.py")
        return
    
    while True:
        try:
            action = questionary.select(
                "What would you like to do?",
                choices=[
                    "🔄 Full Data Sync (Interactive)",
                    "⚡ Quick Update (Last 7 days)", 
                    "📊 Show Data Statistics",
                    "📤 Export to Excel",
                    "🧹 Clean Old Data",
                    "🚪 Exit"
                ]
            ).ask()
            
            if action == "🔄 Full Data Sync (Interactive)":
                await fetch_data_interactive()
                
            elif action == "⚡ Quick Update (Last 7 days)":
                await quick_update()
                
            elif action == "📊 Show Data Statistics":
                show_data_stats()
                
            elif action == "📤 Export to Excel":
                export_to_excel()
                
            elif action == "🧹 Clean Old Data":
                data_service = DataService()
                stats = data_service.cleanup_old_data(365)
                print(f"Cleaned up {stats['expired_cache_entries']} expired cache entries")
                
            elif action == "🚪 Exit":
                print(f"\n{Fore.GREEN}👋 Goodbye!{Style.RESET_ALL}")
                break
            
            print("\n" + "="*60)
            
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}👋 Operation interrupted{Style.RESET_ALL}")
            break
        except Exception as e:
            print(f"\n{Fore.RED}❌ Unexpected error: {e}{Style.RESET_ALL}")


if __name__ == "__main__":
    asyncio.run(main())