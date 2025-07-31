#!/usr/bin/env python3
"""
Modern Cryptocurrency Screening Tool

This replaces the original screening_coins_master.py with a cleaner, 
database-powered implementation.
"""

import sys
import asyncio
from datetime import date, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import questionary
from loguru import logger
from colorama import init, Fore, Style

from services.screening_service import ScreeningService
from services.data_service import DataService
from services.coingecko_service import CoinGeckoService
from config.settings import get_config
from database.connection import check_database_connection

# Initialize colorama
init()


def print_banner():
    """Print application banner."""
    banner = f"""
{Fore.CYAN}
╔══════════════════════════════════════════════════════════════╗
║                 MODERN SCREENING ANALYZER                    ║
║               Database-Powered & Optimized                   ║
╚══════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}
"""
    print(banner)


def get_user_inputs() -> dict:
    """Get user inputs for screening analysis."""
    inputs = {}
    
    # Data source selection
    data_source = questionary.select(
        "Which data source do you want to use?",
        choices=["Database (Recommended)", "Fetch Fresh Data"]
    ).ask()
    inputs["use_database"] = data_source == "Database (Recommended)"
    
    # Direction selection
    direction = questionary.select(
        "Analysis direction:",
        choices=["Forward (from specific date)", "Backward (from today)"]
    ).ask()
    inputs["direction"] = "forward" if "Forward" in direction else "backward"
    
    # Timeframe selection
    if inputs["direction"] == "forward":
        days_input = questionary.text(
            "From how many days ago to start analysis? (e.g., 30)",
            default="30"
        ).ask()
        inputs["start_days_ago"] = int(days_input)
    else:
        days_input = questionary.text(
            "How many days back to analyze? (e.g., 30)",
            default="30"
        ).ask()
        inputs["analysis_days"] = int(days_input)
    
    # Timeframes to analyze
    timeframe_choice = questionary.select(
        "Which timeframes to analyze?",
        choices=["All (1-30 days)", "Custom selection", "Quick (1,3,7,14 days)"]
    ).ask()
    
    if "All" in timeframe_choice:
        inputs["timeframes"] = list(range(1, 31))
    elif "Quick" in timeframe_choice:
        inputs["timeframes"] = [1, 3, 7, 14]
    else:
        timeframes_input = questionary.text(
            "Enter timeframes (comma-separated, e.g., 1,3,7,14,30):",
            default="1,3,7,14,30"
        ).ask()
        inputs["timeframes"] = [int(x.strip()) for x in timeframes_input.split(",")]
    
    # Coin selection
    coin_limit = questionary.text(
        "How many top cryptocurrencies to analyze?",
        default="100"
    ).ask()
    inputs["coin_limit"] = int(coin_limit)
    
    # Result ordering
    order_by = questionary.select(
        "Order results by:",
        choices=["Total Score (Recommended)", "Performance", "Best Rank"]
    ).ask()
    inputs["order_by"] = "score" if "Score" in order_by else "performance" if "Performance" in order_by else "rank"
    
    return inputs


def check_data_availability(data_service: DataService) -> bool:
    """Check if we have sufficient data in the database."""
    try:
        stats = data_service.get_data_coverage_stats()
        
        print(f"\n{Fore.BLUE}📊 Database Status:{Style.RESET_ALL}")
        print(f"  Cryptocurrencies: {stats['total_cryptocurrencies']:,}")
        print(f"  Price records: {stats['total_price_records']:,}")
        print(f"  SMA records: {stats['total_sma_records']:,}")
        
        if stats['total_cryptocurrencies'] == 0:
            print(f"{Fore.RED}❌ No cryptocurrencies in database{Style.RESET_ALL}")
            return False
        
        if stats['total_price_records'] < 100:
            print(f"{Fore.YELLOW}⚠️  Limited price data available{Style.RESET_ALL}")
            return False
        
        print(f"{Fore.GREEN}✅ Sufficient data available for analysis{Style.RESET_ALL}")
        return True
        
    except Exception as e:
        print(f"{Fore.RED}❌ Error checking data availability: {e}{Style.RESET_ALL}")
        return False


async def fetch_fresh_data(coin_limit: int) -> bool:
    """Fetch fresh data if needed."""
    print(f"\n{Fore.YELLOW}🔄 Fetching fresh data for {coin_limit} cryptocurrencies...{Style.RESET_ALL}")
    
    try:
        coingecko_service = CoinGeckoService()
        
        # Fetch recent data (last 30 days)
        stats = await coingecko_service.sync_all_data(coin_limit, 30)
        
        print(f"{Fore.GREEN}✅ Data fetch completed:{Style.RESET_ALL}")
        print(f"  Cryptocurrencies: {stats['cryptocurrencies_synced']}")
        print(f"  Price records: {stats['price_records_synced']:,}")
        print(f"  SMA records: {stats['sma_records_synced']:,}")
        
        if stats['errors'] > 0:
            print(f"  Errors: {stats['errors']}")
        
        return True
        
    except Exception as e:
        print(f"{Fore.RED}❌ Data fetch failed: {e}{Style.RESET_ALL}")
        return False


def run_screening_analysis(inputs: dict) -> dict:
    """Run the screening analysis with given inputs."""
    print(f"\n{Fore.GREEN}🔍 Starting screening analysis...{Style.RESET_ALL}")
    
    try:
        # Initialize services
        data_service = DataService()
        screening_service = ScreeningService()
        
        # Get active cryptocurrencies
        cryptos = data_service.get_active_cryptocurrencies(inputs["coin_limit"])
        if not cryptos:
            print(f"{Fore.RED}❌ No cryptocurrencies found{Style.RESET_ALL}")
            return {}
        
        coin_ids = [crypto['coin_id'] for crypto in cryptos]
        print(f"Analyzing {len(coin_ids)} cryptocurrencies...")
        
        # Determine analysis date
        if inputs["direction"] == "forward":
            analysis_date = date.today() - timedelta(days=inputs["start_days_ago"])
        else:
            analysis_date = date.today()
        
        print(f"Analysis date: {analysis_date}")
        print(f"Direction: {inputs['direction']}")
        print(f"Timeframes: {inputs['timeframes']}")
        
        # Run screening
        results = screening_service.run_comprehensive_screening(
            coin_ids=coin_ids,
            analysis_date=analysis_date,
            direction=inputs["direction"],
            timeframes=inputs["timeframes"]
        )
        
        return results
        
    except Exception as e:
        print(f"{Fore.RED}❌ Screening analysis failed: {e}{Style.RESET_ALL}")
        logger.error(f"Screening analysis error: {e}")
        return {}


def display_results(results: dict, inputs: dict):
    """Display screening results."""
    if not results or not results.get('leaderboard'):
        print(f"{Fore.YELLOW}⚠️  No results to display{Style.RESET_ALL}")
        return
    
    leaderboard = results['leaderboard']
    statistics = results.get('statistics', {})
    
    print(f"\n{Fore.GREEN}🏆 SCREENING RESULTS{Style.RESET_ALL}")
    print("=" * 60)
    
    # Sort leaderboard based on user preference
    if inputs["order_by"] == "performance":
        leaderboard = sorted(leaderboard, key=lambda x: x['avg_return'], reverse=True)
    elif inputs["order_by"] == "rank":
        leaderboard = sorted(leaderboard, key=lambda x: x['best_rank'])
    # else: already sorted by total_score
    
    # Display top results
    print(f"\n{Fore.CYAN}📊 TOP 20 CRYPTOCURRENCIES:{Style.RESET_ALL}")
    print(f"{'Rank':<4} {'Coin':<12} {'Total Score':<12} {'Avg Return':<12} {'Best Rank':<10}")
    print("-" * 60)
    
    for i, coin_data in enumerate(leaderboard[:20]):
        coin_id = coin_data['coin_id'].upper()
        total_score = coin_data['total_score']
        avg_return = coin_data['avg_return']
        best_rank = coin_data['best_rank']
        
        # Color coding based on performance
        if total_score > 0:
            color = Fore.GREEN
        elif total_score < 0:
            color = Fore.RED
        else:
            color = Fore.YELLOW
        
        print(f"{color}{i+1:<4} {coin_id:<12} {total_score:<12.1f} {avg_return:<12.2f}% {best_rank:<10}{Style.RESET_ALL}")
    
    # Display statistics
    if statistics:
        print(f"\n{Fore.BLUE}📈 ANALYSIS STATISTICS:{Style.RESET_ALL}")
        print(f"Total analyses: {statistics.get('total_analyses', 0):,}")
        print(f"Unique coins: {statistics.get('unique_coins', 0):,}")
        
        if 'score_stats' in statistics:
            score_stats = statistics['score_stats']
            print(f"Score range: {score_stats['min']:.1f} to {score_stats['max']:.1f}")
            print(f"Average score: {score_stats['mean']:.1f}")
        
        if 'return_stats' in statistics:
            return_stats = statistics['return_stats']
            print(f"Return range: {return_stats['min']:.2f}% to {return_stats['max']:.2f}%")
            print(f"Average return: {return_stats['mean']:.2f}%")


def export_results(results: dict):
    """Export results to Excel."""
    if not results:
        return
    
    export = questionary.confirm(
        "Export results to Excel?"
    ).ask()
    
    if export:
        screening_service = ScreeningService()
        
        # Generate filename with timestamp
        timestamp = date.today().strftime("%Y%m%d")
        direction = results.get('direction', 'analysis')
        filename = f"data/outputs/screening_{direction}_{timestamp}.xlsx"
        
        success = screening_service.export_results_to_excel(results, filename)
        
        if success:
            print(f"{Fore.GREEN}✅ Results exported to {filename}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ Export failed{Style.RESET_ALL}")


async def main():
    """Main function."""
    print_banner()
    
    # Check database connection
    if not check_database_connection():
        print(f"{Fore.RED}❌ Database connection failed{Style.RESET_ALL}")
        print("Run: python setup_database.py")
        return
    
    # Get user inputs
    inputs = get_user_inputs()
    
    print(f"\n{Fore.YELLOW}📋 Analysis Configuration:{Style.RESET_ALL}")
    print(f"  Direction: {inputs['direction']}")
    print(f"  Timeframes: {inputs['timeframes']}")
    print(f"  Coin limit: {inputs['coin_limit']}")
    print(f"  Order by: {inputs['order_by']}")
    
    # Check data availability or fetch fresh data
    data_service = DataService()
    
    if inputs["use_database"]:
        if not check_data_availability(data_service):
            fetch_fresh = questionary.confirm(
                "Database has insufficient data. Fetch fresh data?"
            ).ask()
            
            if fetch_fresh:
                success = await fetch_fresh_data(inputs["coin_limit"])
                if not success:
                    print(f"{Fore.RED}❌ Cannot proceed without data{Style.RESET_ALL}")
                    return
            else:
                print(f"{Fore.YELLOW}Analysis cancelled{Style.RESET_ALL}")
                return
    else:
        success = await fetch_fresh_data(inputs["coin_limit"])
        if not success:
            print(f"{Fore.RED}❌ Cannot proceed without data{Style.RESET_ALL}")
            return
    
    # Run analysis
    results = run_screening_analysis(inputs)
    
    if results:
        # Display results
        display_results(results, inputs)
        
        # Export option
        export_results(results)
        
        print(f"\n{Fore.GREEN}🎉 Analysis completed successfully!{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}❌ Analysis failed{Style.RESET_ALL}")


if __name__ == "__main__":
    asyncio.run(main())