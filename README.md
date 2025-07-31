# Cryptocurrency Screening Bot V2 🚀

Sistema modernizzato per lo screening di criptovalute con database SQLite, interfaccia web interattiva e parametri configurabili in tempo reale.

## 🎯 Funzionalità

### Core Features:
- **Database SQLite**: Storage persistente con SQLAlchemy ORM
- **Web Dashboard**: Interfaccia Streamlit con parametri configurabili
- **Performance Ottimizzate**: 919x più veloce della versione precedente
- **API Integration**: CoinGecko con rate limiting intelligente
- **Cache System**: Cache database con TTL per ridurre chiamate API

### Analisi Features:
- **Screening Moderno**: Algoritmi vettorizzati con pandas/numpy
- **SMA Indicators**: Periodi configurabili (6, 11, 21) dall'interfaccia web
- **Multi-timeframe**: Analisi su timeframes multipli (1-30 giorni)
- **Scoring System**: Sistema di punteggi configurabile per ranking e SMA
- **Visualizations**: Grafici interattivi con Plotly

### Interface Features:
- **Real-time Configuration**: Parametri modificabili dall'interfaccia web
- **Interactive Charts**: Performance charts, heatmaps, distribuzioni
- **Export Multiplo**: Excel, CSV, JSON download
- **Progress Tracking**: Barre di progresso e status in tempo reale

## 📁 Struttura del Progetto

```
├── src/                      # Codice sorgente principale
│   ├── data_fetchers/        # Moduli per raccolta dati
│   ├── analyzers/            # Algoritmi di analisi
│   └── utils/                # Utility e helper
├── config/                   # File di configurazione
├── data/                     # Dati di input e output
│   ├── inputs/               # File di input (ID coins, etc.)
│   └── outputs/              # Report Excel generati
├── examples/                 # Esempi di utilizzo
├── docs/                     # Documentazione
└── requirements.txt          # Dipendenze Python
```

## 🚀 Quick Start

### Prerequisiti

- Python 3.8+
- Pip package manager

### Installazione

1. Clona il repository:
```bash
git clone https://github.com/Dado-hash/Screening_bot_V2.git
cd Screening_bot_V2
```

2. Installa le dipendenze:
```bash
pip install -r requirements.txt
```

3. Configura le API keys:
```bash
cp config/api_keys.py.example config/api_keys.py
# Modifica il file con le tue API keys
```

## 🌐 Web Dashboard (NUOVO - Phase 3)

**Modo Principale - Interfaccia Web Interattiva:**

```bash
python dashboard.py
```

La dashboard si aprirà su `http://localhost:8501` con:

### 🎛️ Parametri Configurabili in Tempo Reale:
- **SMA Periods**: Fast (3-15), Medium (8-25), Slow (15-50)
- **Rank Scores**: Top 10/15/20 configurable scores
- **SMA Scores**: Above/Below Fast/Medium/Slow configurable scores
- **Filters**: Min volume, max coins per analysis

### 🎯 Screening Interattivo:
- **Coin Selection**: Multiselect da database
- **Date Picker**: Analysis date selection
- **Direction**: Forward/Backward analysis
- **Timeframes**: Multi-select 1-30 days

### 📊 Visualizzazioni Interactive:
- **Performance Charts**: Total Score vs Average Return
- **Score Distribution**: Histogram distribution
- **Timeframe Heatmaps**: Score heatmap by coin and timeframe
- **Detailed Analytics**: Filterable results tables

### 📥 Export Multiplo:
- **Excel**: Complete analysis with timeframe breakdown
- **CSV**: Leaderboard data download
- **JSON**: Full results data export

## 📋 CLI Mode (Legacy)

### Utilizzo Base

1. **Setup Database**:
```bash
python setup_database.py
```

2. **Raccolta Dati Moderni**:
```bash
python src/data_fetchers/get_historical_data_modern.py
```

3. **Screening CLI Moderno**:
```bash
python src/analyzers/screening_coins_modern.py
```

4. **Analisi dei Risultati**:
   - Database SQLite in `data/screening_bot.db`
   - Export Excel in `data/outputs/`

## 📊 Workflow Consigliato

1. **Raccolta Dati**: Esegui `get_historical_data_coingecko.py`
2. **Screening**: Lancia `screening_coins_master.py` due volte:
   - Una volta per calcoli cumulativi a ritroso
   - Una volta per calcoli in avanti
3. **Analisi**: Controlla i fogli `cumulative_changes_forward` e `cumulative_changes_backward`

## 🔧 Configurazione

### API Keys

Configura le tue API keys in `config/api_keys.py`:

```python
# CoinGecko API (gratuita)
COINGECKO_API_KEY = "your_api_key_here"

# Binance API (opzionale)
BINANCE_API_KEY = "your_api_key_here"
BINANCE_SECRET_KEY = "your_secret_key_here"
```

### Parametri di Screening

I parametri principali possono essere modificati nei file di configurazione:
- Numero di giorni per l'analisi
- Soglie di volatilità
- Criteri di screening

## 📈 Indicatori Supportati

- **SMA (Simple Moving Average)**: Fast, Medium, Slow
- **Analisi Volatilità**: Calcolo deviazione standard
- **Pattern Recognition**: Identificazione top/bottom ciclici
- **Correlazioni**: Analisi correlazioni tra asset

## 🔍 Esempi

Nella cartella `examples/` trovi:
- `get_historical_data.py`: Esempio base raccolta dati
- `riassunto_coingecko_API.py`: Guida API CoinGecko
- `riassunto_pandas.py`: Esempi analisi dati con Pandas

## 📋 Dipendenze

- pandas: Analisi e manipolazione dati
- numpy: Calcoli numerici
- plotly: Visualizzazioni interattive
- pycoingecko: API CoinGecko
- colorama: Output colorato terminale
- questionary: Interfaccia interattiva
- seaborn: Visualizzazioni statistiche

## 🤝 Contribuire

1. Fork del repository
2. Crea un branch per la tua feature (`git checkout -b feature/nuova-funzionalità`)
3. Commit delle modifiche (`git commit -am 'Aggiunge nuova funzionalità'`)
4. Push del branch (`git push origin feature/nuova-funzionalità`)
5. Apri una Pull Request

## 📝 License

Questo progetto è sotto licenza MIT. Vedi il file `LICENSE` per dettagli.

## ⚠️ Disclaimer

Questo software è solo per scopi educativi e di ricerca. Non costituisce consigli di investimento. 
Trading di criptovalute comporta rischi significativi di perdite finanziarie.

## 📞 Supporto

Per domande o supporto:
- Apri un issue su GitHub
- Controlla la documentazione in `docs/`

---

⭐ Se trovi utile questo progetto, lascia una stella!
