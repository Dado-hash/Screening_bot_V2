# Configurazione locale per sviluppo
# Non committare questo file!

# Parametri di default per testing
DEFAULT_DAYS = 30
DEFAULT_COINS_LIMIT = 50
DEFAULT_VS_CURRENCY = "usd"

# Impostazioni cache
CACHE_ENABLED = True
CACHE_DURATION_HOURS = 24

# Logging
LOG_LEVEL = "INFO"
LOG_TO_FILE = True
LOG_FILE = "logs/screening_bot.log"

# Rate limiting
API_DELAY_SECONDS = 1
MAX_RETRIES = 3

# Percorsi
DATA_DIR = "data"
OUTPUT_DIR = "data/outputs"
INPUT_DIR = "data/inputs"
CACHE_DIR = "cache"

# Features sperimentali
ENABLE_EXPERIMENTAL_FEATURES = False
USE_ADVANCED_INDICATORS = False
