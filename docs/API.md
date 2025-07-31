# API Documentation

## CoinGecko API

### Panoramica
CoinGecko fornisce dati completi su criptovalute, inclusi prezzi storici, volumi e statistiche di mercato.

### Configurazione
```python
from pycoingecko import CoinGeckoAPI
cg = CoinGeckoAPI()
```

### Endpoints Utilizzati

#### 1. Get Historical Data
```python
# Ottieni dati storici per una specifica criptovaluta
data = cg.get_coin_market_chart_by_id(
    id='bitcoin',
    vs_currency='usd',
    days=30
)
```

#### 2. Get Coin List
```python
# Lista di tutte le criptovalute disponibili
coins = cg.get_coins_list()
```

### Rate Limits
- **Free Plan**: 10-30 chiamate/minuto
- **Pro Plan**: Rate limits più alti disponibili

### Gestione Errori
```python
try:
    data = cg.get_coin_market_chart_by_id(id='bitcoin', vs_currency='usd', days=30)
except Exception as e:
    print(f"Errore API CoinGecko: {e}")
```

## Binance API

### Panoramica
Binance API fornisce dati di trading in tempo reale e storici dal più grande exchange di criptovalute.

### Configurazione
```python
from binance.client import Client
client = Client(api_key, api_secret)
```

### Endpoints Utilizzati

#### 1. Get Historical Klines
```python
# Dati storici candlestick
klines = client.get_historical_klines(
    "BTCUSDT", 
    Client.KLINE_INTERVAL_1DAY, 
    "30 days ago UTC"
)
```

#### 2. Get Symbol Ticker
```python
# Prezzo attuale di un simbolo
ticker = client.get_symbol_ticker(symbol="BTCUSDT")
```

### Rate Limits
- **Weight**: Ogni richiesta ha un peso
- **Limite**: 1200 weight per minuto
- **Monitoraggio**: Headers di risposta mostrano utilizzo

### Gestione Errori
```python
from binance.exceptions import BinanceAPIException
try:
    data = client.get_historical_klines("BTCUSDT", "1d", "30 days ago")
except BinanceAPIException as e:
    print(f"Errore API Binance: {e}")
```

## Best Practices

### 1. Rate Limiting
```python
import time

def api_call_with_retry(api_function, *args, max_retries=3, **kwargs):
    for attempt in range(max_retries):
        try:
            return api_function(*args, **kwargs)
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(2 ** attempt)  # Exponential backoff
```

### 2. Caching
```python
import pickle
from datetime import datetime, timedelta

def cache_data(data, filename, hours=24):
    cache_data = {
        'timestamp': datetime.now(),
        'data': data
    }
    with open(f'cache/{filename}.pkl', 'wb') as f:
        pickle.dump(cache_data, f)

def load_cached_data(filename, hours=24):
    try:
        with open(f'cache/{filename}.pkl', 'rb') as f:
            cache_data = pickle.load(f)
        
        if datetime.now() - cache_data['timestamp'] < timedelta(hours=hours):
            return cache_data['data']
    except FileNotFoundError:
        pass
    return None
```

### 3. Error Handling
```python
class APIError(Exception):
    pass

def safe_api_call(api_function, *args, **kwargs):
    try:
        return api_function(*args, **kwargs)
    except Exception as e:
        print(f"Errore API: {e}")
        raise APIError(f"Fallimento chiamata API: {e}")
```

## Sicurezza

### API Keys
- Non committare mai API keys nel codice
- Usa variabili d'ambiente per production
- Limita i permessi delle API keys al minimo necessario

### Esempio Sicuro
```python
import os
from config.api_keys import COINGECKO_API_KEY

# In production, usa variabili d'ambiente
api_key = os.getenv('COINGECKO_API_KEY', COINGECKO_API_KEY)
```

## Monitoraggio

### Logging delle API Calls
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_api_call(api_name, endpoint, status):
    logger.info(f"API Call - {api_name} - {endpoint} - Status: {status}")
```

### Metriche
- Numero di chiamate per minuto
- Tasso di successo/fallimento
- Latenza media delle risposte
