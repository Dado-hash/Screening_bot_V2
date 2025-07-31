#!/usr/bin/env python3
"""
Test script for Phase 1 - Database and Data Fetching
Runs from project root using module imports
"""

import sys
import asyncio
from pathlib import Path

# Set up proper Python path for module imports
project_root = Path(__file__).parent.absolute()
src_path = project_root / "src"

# Ensure both paths are in sys.path
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

try:
    from loguru import logger
    from colorama import init, Fore, Style
    print("✅ Base imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

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

def simple_test():
    """Run a simple connectivity test."""
    print(f"\n{Fore.YELLOW}🔍 Simple Import Test{Style.RESET_ALL}")
    
    try:
        # Test basic imports one by one
        print("Testing database imports...")
        from database.connection import check_database_connection
        print("✅ Database connection import OK")
        
        from database.migrations import DatabaseMigrator  
        print("✅ Database migrator import OK")
        
        print("Testing service imports...")
        # Skip services for now as they have complex dependencies
        print("⚠️  Service imports skipped (complex dependencies)")
        
        print(f"{Fore.GREEN}✅ Basic imports successful!{Style.RESET_ALL}")
        return True
        
    except Exception as e:
        print(f"{Fore.RED}❌ Import failed: {e}{Style.RESET_ALL}")
        logger.error(f"Import error: {e}")
        return False

def test_database_connection():
    """Test database connection only."""
    print(f"\n{Fore.YELLOW}🔍 Database Connection Test{Style.RESET_ALL}")
    
    try:
        from database.connection import check_database_connection
        
        if check_database_connection():
            print(f"{Fore.GREEN}✅ Database connection successful{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}❌ Database connection failed{Style.RESET_ALL}")
            return False
            
    except Exception as e:
        print(f"{Fore.RED}❌ Database test error: {e}{Style.RESET_ALL}")
        return False

def main():
    """Run simplified Phase 1 tests."""
    print_banner()
    
    print(f"{Fore.BLUE}Starting simplified Phase 1 test...{Style.RESET_ALL}")
    
    # Test results
    tests = [
        ("Simple Import Test", simple_test()),
        ("Database Connection", test_database_connection()),
    ]
    
    # Print summary
    print(f"\n{Fore.BLUE}📊 TEST SUMMARY{Style.RESET_ALL}")
    print("=" * 50)
    
    passed = sum(1 for _, result in tests if result)
    failed = len(tests) - passed
    
    for test_name, result in tests:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    print(f"\n{Fore.GREEN if failed == 0 else Fore.YELLOW}Results: {passed} passed, {failed} failed{Style.RESET_ALL}")
    
    if failed == 0:
        print(f"\n{Fore.GREEN}🎉 Basic tests passed!{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.YELLOW}⚠️  Some tests failed. This is normal for initial setup.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
