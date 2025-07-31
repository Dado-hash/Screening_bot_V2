#!/usr/bin/env python3
"""
Test script for Phase 3 - Web Dashboard implementation.
Verifies that dashboard components are working correctly.
"""

import sys
import os
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

def test_dashboard_imports():
    """Test that dashboard can be imported correctly."""
    print("🧪 Testing dashboard imports...")
    
    try:
        from dashboard.app import ScreeningDashboard
        print("✅ ScreeningDashboard import successful")
        
        # Test initialization
        dashboard = ScreeningDashboard()
        print("✅ Dashboard initialization successful")
        
        # Check configuration
        config = dashboard.config
        print(f"✅ Configuration loaded: {config.environment}")
        
        # Check services
        screening_service = dashboard.screening_service
        print(f"✅ ScreeningService loaded with config: {type(screening_service.config).__name__}")
        
        return True
        
    except Exception as e:
        print(f"❌ Dashboard import failed: {e}")
        return False

def test_streamlit_availability():
    """Test that Streamlit is available."""
    print("\n🧪 Testing Streamlit availability...")
    
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
        
        import plotly.express as px
        import plotly.graph_objects as go
        print("✅ Plotly imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Required packages missing: {e}")
        return False

def test_existing_services():
    """Test that existing services are working."""
    print("\n🧪 Testing existing services integration...")
    
    try:
        from services.screening_service import ScreeningService
        from config.settings import get_config, ScreeningConfig
        
        config = get_config()
        print(f"✅ Configuration loaded: {config.environment}")
        
        screening_service = ScreeningService()
        print("✅ ScreeningService initialized")
        
        # Test configuration customization
        custom_config = ScreeningConfig(
            sma_fast=8,
            sma_medium=15,
            sma_slow=25
        )
        
        screening_service.config = custom_config
        print("✅ Custom configuration applied")
        print(f"   SMA Fast: {screening_service.config.sma_fast}")
        print(f"   SMA Medium: {screening_service.config.sma_medium}")
        print(f"   SMA Slow: {screening_service.config.sma_slow}")
        
        return True
        
    except Exception as e:
        print(f"❌ Services test failed: {e}")
        return False

def test_database_connection():
    """Test database connectivity."""
    print("\n🧪 Testing database connection...")
    
    try:
        from database.connection import DatabaseTransaction
        from repositories.cryptocurrency import CryptocurrencyRepository
        
        with DatabaseTransaction() as session:
            crypto_repo = CryptocurrencyRepository(session)
            cryptos = crypto_repo.get_all()
            print(f"✅ Database connected, found {len(cryptos)} cryptocurrencies")
            
            if cryptos:
                sample_coins = [crypto.coin_id for crypto in cryptos[:5]]
                print(f"   Sample coins: {sample_coins}")
            
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_file_structure():
    """Test that all required files exist."""
    print("\n🧪 Testing file structure...")
    
    required_files = [
        "src/dashboard/__init__.py",
        "src/dashboard/app.py",
        "dashboard.py",
        "requirements.txt"
    ]
    
    missing_files = []
    
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            missing_files.append(file_path)
    
    return len(missing_files) == 0

def main():
    """Run all Phase 3 tests."""
    print("🚀 Phase 3 Implementation Test")
    print("=" * 50)
    
    test_results = []
    
    # Run tests
    test_results.append(("File Structure", test_file_structure()))
    test_results.append(("Streamlit Availability", test_streamlit_availability()))
    test_results.append(("Existing Services", test_existing_services()))
    test_results.append(("Database Connection", test_database_connection()))
    test_results.append(("Dashboard Imports", test_dashboard_imports()))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Phase 3 implementation is ready!")
        print("\n🚀 To launch the dashboard:")
        print("   python dashboard.py")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)