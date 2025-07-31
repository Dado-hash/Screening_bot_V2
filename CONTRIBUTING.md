# Contributing to Screening Bot V2

Prima di tutto, grazie per il tuo interesse nel contribuire al progetto! 🎉

## Come contribuire

### Segnalazione di bug

Se trovi un bug, per favore crea un issue con:
- Una descrizione dettagliata del problema
- I passi per riprodurre il bug
- Il comportamento atteso vs quello osservato
- La versione di Python e del sistema operativo utilizzato

### Proposte di nuove funzionalità

Per proporre nuove funzionalità:
1. Controlla prima se esiste già un issue simile
2. Crea un nuovo issue descrivendo la funzionalità
3. Spiega perché sarebbe utile
4. Fornisci dettagli implementativi se possibile

### Pull Requests

1. **Fork** il repository
2. **Crea un branch** per la tua feature:
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Fai le tue modifiche** seguendo le linee guida del codice
4. **Aggiungi test** per le nuove funzionalità
5. **Assicurati** che tutti i test passino:
   ```bash
   make test
   ```
6. **Formatta il codice**:
   ```bash
   make format
   ```
7. **Controlla il linting**:
   ```bash
   make lint
   ```
8. **Commit** le tue modifiche con messaggi chiari
9. **Push** al tuo fork
10. **Apri una Pull Request**

## Linee guida per il codice

### Stile del codice
- Usa [Black](https://black.readthedocs.io/) per la formattazione (max 88 caratteri per riga)
- Segui [PEP 8](https://pep8.org/) per lo stile Python
- Usa [flake8](https://flake8.pycqa.org/) per il linting

### Documentazione
- Aggiungi docstring per tutte le funzioni pubbliche
- Usa type hints quando possibile
- Aggiorna il README.md se necessario

### Test
- Scrivi test per tutte le nuove funzionalità
- Mantieni una copertura dei test > 80%
- Usa pytest per i test

### Messaggi di commit
Usa messaggi di commit chiari e descrittivi:
```
feat: aggiungi supporto per nuova API
fix: risolvi problema di connessione al database
docs: aggiorna README con nuove istruzioni
test: aggiungi test per calcolo performance
```

## Configurazione dell'ambiente di sviluppo

1. **Clona il repository**:
   ```bash
   git clone https://github.com/Dado-hash/Screening_bot_V2.git
   cd Screening_bot_V2
   ```

2. **Crea un ambiente virtuale**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # oppure
   venv\Scripts\activate  # Windows
   ```

3. **Installa le dipendenze**:
   ```bash
   make install
   ```

4. **Configura il database di test**:
   ```bash
   createdb screeningbot_test
   ```

5. **Esegui i test**:
   ```bash
   make test
   ```

## Processo di review

1. Tutte le PR devono passare i controlli automatici (CI)
2. Almeno un maintainer deve approvare la PR
3. Il codice deve essere ben documentato e testato
4. Le modifiche breaking devono essere chiaramente indicate

## Domande?

Se hai domande, non esitare a:
- Aprire un issue per discussioni pubbliche
- Contattare i maintainer

Grazie per il tuo contributo! 🚀
