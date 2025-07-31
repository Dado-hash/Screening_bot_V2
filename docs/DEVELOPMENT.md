# Cryptocurrency Screening Bot V2 - Development Setup

## Setup Ambiente di Sviluppo

### 1. Python Environment

Crea un ambiente virtuale:

```bash
python -m venv venv
source venv/bin/activate  # Su macOS/Linux
# oppure
venv\Scripts\activate     # Su Windows
```

### 2. Installazione Dipendenze

```bash
pip install -r requirements.txt
```

### 3. Configurazione API Keys

1. Copia il file di esempio:
```bash
cp config/api_keys.py.example config/api_keys.py
```

2. Modifica `config/api_keys.py` con le tue API keys reali

### 4. Struttura File di Input

Assicurati che i file di input siano presenti:
- `data/inputs/idcoins`: Lista degli ID delle criptovalute
- `data/inputs/idcoins1`: Lista alternativa degli ID

### 5. Test di Funzionamento

Testa la raccolta dati:
```bash
python src/data_fetchers/get_historical_data_coingecko.py
```

Testa lo screening:
```bash
python src/analyzers/screening_coins_master.py
```

## Workflow di Sviluppo

1. **Fetch data**: Sempre partire raccogliendo dati freschi
2. **Analysis**: Eseguire screening con parametri appropriati  
3. **Review**: Controllare output in `data/outputs/`

## Note Importanti

- I file Excel di output vengono rigenerati ad ogni esecuzione
- Le API keys sono escluse dal git (vedi .gitignore)
- Usa sempre l'ambiente virtuale per lo sviluppo

## Debugging

Per debug dettagliato, modifica i livelli di logging nei file Python.
