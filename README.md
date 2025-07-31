# Cryptocurrency Screening Bot V2 🚀

Un bot avanzato per lo screening e l'analisi di criptovalute con integrazione a CoinGecko e Binance APIs.

## 🎯 Funzionalità

- **Raccolta Dati Storici**: Integrazione con CoinGecko e Binance per dati storici completi
- **Analisi Tecnica**: Calcolo di indicatori tecnici, SMA e analisi della volatilità
- **Screening Automatico**: Identificazione automatica di opportunità di trading
- **Analisi Ciclica**: Rilevamento di pattern e cicli di mercato
- **Report Excel**: Generazione automatica di report dettagliati

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

### Utilizzo Base

1. **Raccolta Dati Storici**:
```bash
python src/data_fetchers/get_historical_data_coingecko.py
```

2. **Screening Principale**:
```bash
python src/analyzers/screening_coins_master.py
```

3. **Analisi dei Risultati**:
   - I risultati sono salvati in `data/outputs/`
   - Controlla i file Excel generati per le analisi

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
