# Screening Bot V2

Un bot automatizzato per l'analisi e il monitoraggio delle performance delle criptovalute, che raccoglie dati storici da Binance e CoinGecko e calcola metriche di performance cumulative.

## 🚀 Caratteristiche

- **Raccolta dati automatica**: Scarica dati storici delle criptovalute da Binance e CoinGecko
- **Analisi performance**: Calcola metriche di performance cumulative per diversi periodi
- **Database PostgreSQL**: Archiviazione sicura e strutturata dei dati
- **Gestione tabelle**: Utility per la gestione e pulizia del database

## 📋 Prerequisiti

- Python 3.8+
- PostgreSQL
- Connessione internet per API calls

## 🛠️ Installazione

1. Clona il repository:
```bash
git clone https://github.com/Dado-hash/Screening_bot_V2.git
cd Screening_bot_V2
```

2. Installa le dipendenze:
```bash
pip install -r requirements.txt
```

3. Configura il database PostgreSQL:
   - Crea un database chiamato `screeningbot`
   - Assicurati che PostgreSQL sia in esecuzione su localhost
   - Modifica le credenziali nel codice se necessario

## 📊 Utilizzo

### Aggiornamento dati storici
```bash
python update_historical_datas.py
```

### Calcolo performance cumulative
```bash
python calculate_performance.py
```

### Pulizia database
```bash
python drop_tables.py
```

## 📁 Struttura del progetto

```
Screening_bot_V2/
├── README.md
├── requirements.txt
├── .gitignore
├── update_historical_datas.py    # Scarica e aggiorna dati storici
├── calculate_performance.py      # Calcola metriche di performance
└── drop_tables.py               # Utility per pulizia database
```

## 🔧 Configurazione

Il bot si connette a un database PostgreSQL locale con le seguenti impostazioni predefinite:
- Host: localhost
- Database: screeningbot
- User: postgres
- Password: dev_password

Per modificare queste impostazioni, aggiorna le stringhe di connessione nei file Python.

## 📈 API utilizzate

- **Binance API**: Per ottenere l'elenco delle criptovalute e dati di trading
- **CoinGecko API**: Per dati storici dettagliati delle criptovalute

## 🤝 Contribuire

1. Fork il progetto
2. Crea un branch per la tua feature (`git checkout -b feature/AmazingFeature`)
3. Commit le tue modifiche (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Apri una Pull Request

## 📝 Licenza

Questo progetto è distribuito sotto la licenza MIT. Vedi `LICENSE` per maggiori informazioni.

## ⚠️ Disclaimer

Questo strumento è solo a scopo educativo e di ricerca. Non costituisce consulenza finanziaria.
