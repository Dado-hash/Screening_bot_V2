"""Configuration settings for the screening system."""

import os
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from pathlib import Path


@dataclass
class DatabaseConfig:
    """Database configuration."""
    url: str = "sqlite:///data/screening_bot.db"
    echo: bool = False
    pool_pre_ping: bool = True
    

@dataclass
class APIConfig:
    """API configuration."""
    coingecko_api_key: Optional[str] = None
    binance_api_key: Optional[str] = None
    binance_secret_key: Optional[str] = None
    rate_limits: Dict[str, int] = None
    
    def __post_init__(self):
        if self.rate_limits is None:
            self.rate_limits = {
                "coingecko": 10,  # requests per minute
                "binance": 1200,
                "default": 60
            }


@dataclass
class ScreeningConfig:
    """Screening algorithm configuration."""
    # Default parameters
    default_days: int = 30
    default_coins_limit: int = 100
    default_vs_currency: str = "btc"
    
    # SMA periods
    sma_fast: int = 6
    sma_medium: int = 11
    sma_slow: int = 21
    
    # Scoring weights
    rank_scores: Dict[str, int] = None
    sma_scores: Dict[str, int] = None
    
    # Performance thresholds
    min_volume_threshold: float = 1000.0  # Minimum daily volume in USD
    max_coins_per_analysis: int = 200
    
    # Analysis parameters
    cumulative_periods: List[int] = None
    direction_options: List[str] = None
    
    def __post_init__(self):
        if self.rank_scores is None:
            self.rank_scores = {
                "top_10": 3,
                "top_15": 2, 
                "top_20": 1,
                "other": 0
            }
        
        if self.sma_scores is None:
            self.sma_scores = {
                "above_fast": 1,
                "above_medium": 2,
                "above_slow": 3,
                "below_fast": -1,
                "below_medium": -2,
                "below_slow": -3
            }
        
        if self.cumulative_periods is None:
            self.cumulative_periods = list(range(1, 31))  # 1 to 30 days
        
        if self.direction_options is None:
            self.direction_options = ["forward", "backward"]


@dataclass
class CacheConfig:
    """Cache configuration."""
    enabled: bool = True
    default_ttl: int = 3600  # 1 hour
    market_data_ttl: int = 3600  # 1 hour
    historical_data_ttl: int = 86400  # 24 hours
    analysis_results_ttl: int = 7200  # 2 hours


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    log_to_file: bool = True
    log_file: str = "logs/screening_bot.log"
    max_log_size: int = 10_000_000  # 10MB
    backup_count: int = 5


@dataclass
class AppConfig:
    """Main application configuration."""
    database: DatabaseConfig
    api: APIConfig
    screening: ScreeningConfig
    cache: CacheConfig
    logging: LoggingConfig
    
    # Paths
    data_dir: str = "data"
    output_dir: str = "data/outputs"
    input_dir: str = "data/inputs"
    cache_dir: str = "cache"
    
    # Environment
    environment: str = "development"  # development, production, testing
    debug: bool = False


def load_config_from_env() -> AppConfig:
    """Load configuration from environment variables and files."""
    
    # Database configuration
    database_config = DatabaseConfig(
        url=os.getenv("DATABASE_URL", "sqlite:///data/screening_bot.db"),
        echo=os.getenv("DATABASE_ECHO", "false").lower() == "true"
    )
    
    # API configuration
    api_config = APIConfig(
        coingecko_api_key=os.getenv("COINGECKO_API_KEY"),
        binance_api_key=os.getenv("BINANCE_API_KEY"),
        binance_secret_key=os.getenv("BINANCE_SECRET_KEY")
    )
    
    # Try to load API keys from config file
    try:
        config_path = Path(__file__).parent.parent.parent / "config" / "api_keys.py"
        if config_path.exists():
            import sys
            sys.path.insert(0, str(config_path.parent))
            try:
                import api_keys
                if hasattr(api_keys, 'COINGECKO_API_KEY') and not api_config.coingecko_api_key:
                    api_config.coingecko_api_key = api_keys.COINGECKO_API_KEY
                if hasattr(api_keys, 'BINANCE_API_KEY') and not api_config.binance_api_key:
                    api_config.binance_api_key = api_keys.BINANCE_API_KEY
                if hasattr(api_keys, 'BINANCE_SECRET_KEY') and not api_config.binance_secret_key:
                    api_config.binance_secret_key = api_keys.BINANCE_SECRET_KEY
            except ImportError:
                pass  # Config file doesn't exist or has errors
    except Exception:
        pass  # Ignore config loading errors
    
    # Screening configuration
    screening_config = ScreeningConfig(
        default_days=int(os.getenv("DEFAULT_DAYS", "30")),
        default_coins_limit=int(os.getenv("DEFAULT_COINS_LIMIT", "100"))
    )
    
    # Cache configuration
    cache_config = CacheConfig(
        enabled=os.getenv("CACHE_ENABLED", "true").lower() == "true",
        default_ttl=int(os.getenv("CACHE_TTL", "3600"))
    )
    
    # Logging configuration
    logging_config = LoggingConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        log_to_file=os.getenv("LOG_TO_FILE", "true").lower() == "true",
        log_file=os.getenv("LOG_FILE", "logs/screening_bot.log")
    )
    
    # Main app configuration
    app_config = AppConfig(
        database=database_config,
        api=api_config,
        screening=screening_config,
        cache=cache_config,
        logging=logging_config,
        environment=os.getenv("ENVIRONMENT", "development"),
        debug=os.getenv("DEBUG", "false").lower() == "true"
    )
    
    return app_config


# Global configuration instance
_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = load_config_from_env()
    return _config


def reload_config() -> AppConfig:
    """Reload configuration from environment."""
    global _config
    _config = load_config_from_env()
    return _config


# Convenience functions
def get_database_config() -> DatabaseConfig:
    """Get database configuration."""
    return get_config().database


def get_api_config() -> APIConfig:
    """Get API configuration."""
    return get_config().api


def get_screening_config() -> ScreeningConfig:
    """Get screening configuration."""
    return get_config().screening


def get_cache_config() -> CacheConfig:
    """Get cache configuration."""
    return get_config().cache