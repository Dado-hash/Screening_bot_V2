# Contributing to Cryptocurrency Screening Bot V2

Grazie per il tuo interesse nel contribuire al progetto! 🎉

## Come Contribuire

### 🐛 Segnalazione Bug

1. Controlla se il bug è già stato segnalato negli [issues](../../issues)
2. Se non esiste, crea un nuovo issue con:
   - Descrizione chiara del problema
   - Passi per riprodurre il bug
   - Comportamento atteso vs comportamento attuale
   - Informazioni sull'ambiente (OS, Python version, etc.)

### 💡 Proposte di Nuove Funzionalità

1. Apri un issue per discutere la funzionalità
2. Descrivi:
   - Il problema che risolve
   - Come dovrebbe funzionare
   - Possibili implementazioni

### 🔧 Pull Requests

1. **Fork** il repository
2. **Crea un branch** per la tua feature:
   ```bash
   git checkout -b feature/nome-feature
   ```
3. **Fai le modifiche** seguendo gli standard del codice
4. **Testa** le modifiche
5. **Commit** con messaggi descrittivi:
   ```bash
   git commit -m "Add: nuova funzionalità per analisi volatilità"
   ```
6. **Push** del branch:
   ```bash
   git push origin feature/nome-feature
   ```
7. **Apri una Pull Request**

## 📋 Standard del Codice

### Python Style Guide

- Segui [PEP 8](https://pep8.org/)
- Usa nomi descrittivi per variabili e funzioni
- Aggiungi docstrings per classi e funzioni
- Mantieni le linee sotto i 100 caratteri

### Esempio di Docstring

```python
def analyze_volatility(prices: List[float], window: int = 20) -> float:
    """
    Calcola la volatilità dei prezzi usando la deviazione standard.
    
    Args:
        prices: Lista dei prezzi da analizzare
        window: Finestra temporale per il calcolo (default: 20)
        
    Returns:
        Volatilità come percentuale
        
    Raises:
        ValueError: Se prices è vuota o window è invalido
    """
    pass
```

### Struttura dei Commit

Usa questo formato per i messaggi di commit:

```
Tipo: breve descrizione (max 50 caratteri)

Descrizione dettagliata se necessaria.
- Cosa è stato cambiato
- Perché è stato cambiato
- Come testare la modifica
```

Tipi di commit:
- `Add`: Nuove funzionalità
- `Fix`: Correzione bug
- `Update`: Aggiornamenti di codice esistente
- `Remove`: Rimozione di codice
- `Docs`: Modifiche alla documentazione
- `Style`: Modifiche di formattazione
- `Refactor`: Refactoring del codice
- `Test`: Aggiunta/modifica test

## 🧪 Testing

Prima di sottomettere una PR:

1. **Testa il codice** su diversi scenari
2. **Verifica** che tutti i file Python siano syntatticamente corretti
3. **Controlla** che non ci siano regressioni nelle funzionalità esistenti

### Test di Base

```bash
# Test sintassi
python -m py_compile src/**/*.py

# Test funzionalità principali
python src/data_fetchers/get_historical_data_coingecko.py
python src/analyzers/screening_coins_master.py
```

## 📚 Documentazione

Se aggiungi nuove funzionalità:

1. **Aggiorna** il README.md se necessario
2. **Aggiungi** esempi in `examples/`
3. **Documenta** nuovi parametri e configurazioni
4. **Includi** commenti nel codice per logiche complesse

## 🎯 Aree di Contributo

Cerchiamo aiuto in particolare su:

- **Nuovi indicatori tecnici**
- **Integrazione con altre API**
- **Miglioramenti UI/UX**
- **Ottimizzazioni performance**
- **Test automatizzati**
- **Documentazione**

## ❓ Domande

Se hai domande:

1. Controlla la [documentazione](docs/)
2. Cerca negli [issues](../../issues) esistenti
3. Apri un nuovo issue con tag "question"

## 🏆 Riconoscimenti

Tutti i contributori saranno aggiunti alla lista dei collaboratori nel README.

---

Grazie per aver contribuito! 🚀
