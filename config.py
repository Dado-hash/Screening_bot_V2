"""
Configuration file for Screening Bot V2
"""
import os
from typing import Dict, Any

# Database configuration
DATABASE_CONFIG: Dict[str, Any] = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'screeningbot'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'dev_password'),
    'port': int(os.getenv('DB_PORT', 5432))
}

# API endpoints
BINANCE_API_URL = os.getenv('BINANCE_API_URL', 'https://api.binance.com')
COINGECKO_API_URL = os.getenv('COINGECKO_API_URL', 'https://api.coingecko.com/api/v3')

# Performance calculation settings
DEFAULT_DAYS = int(os.getenv('DEFAULT_DAYS', 30))
MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
DELAY_BETWEEN_REQUESTS = int(os.getenv('DELAY_BETWEEN_REQUESTS', 1))

# Logging configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
