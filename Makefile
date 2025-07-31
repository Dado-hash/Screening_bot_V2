# Makefile for Cryptocurrency Screening Bot V2

.PHONY: help setup install test lint format clean run-data run-screen status

# Default target
help:
	@echo "Cryptocurrency Screening Bot V2 - Commands"
	@echo "=========================================="
	@echo "setup     - Setup completo del progetto"
	@echo "install   - Installa dipendenze"
	@echo "test      - Esegue test di base"
	@echo "lint      - Controllo sintassi con flake8"
	@echo "format    - Formatta codice con black"
	@echo "clean     - Pulisce file temporanei"
	@echo "run-data  - Raccoglie dati storici"
	@echo "run-screen- Esegue screening"
	@echo "status    - Mostra status del progetto"
	@echo "run       - Esegue il bot interattivo"

# Setup completo
setup:
	@echo "🚀 Setup del progetto..."
	./setup.sh

# Installazione dipendenze
install:
	@echo "📚 Installazione dipendenze..."
	pip install -r requirements.txt

# Test di base
test:
	@echo "🧪 Test sintassi..."
	python -m py_compile src/data_fetchers/*.py
	python -m py_compile src/analyzers/*.py
	python -c "import sys; sys.path.append('src'); print('✅ Import test OK')"

# Lint
lint:
	@echo "🔍 Controllo sintassi..."
	flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 src/ --count --exit-zero --max-complexity=10 --max-line-length=100 --statistics

# Format
format:
	@echo "🎨 Formattazione codice..."
	black src/ --line-length=100
	isort src/

# Pulizia
clean:
	@echo "🧹 Pulizia file temporanei..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.log" -delete
	rm -rf .pytest_cache/
	rm -rf cache/*

# Esecuzione raccolta dati
run-data:
	@echo "🔄 Raccolta dati..."
	python src/data_fetchers/get_historical_data_coingecko.py

# Esecuzione screening
run-screen:
	@echo "📊 Screening..."
	python src/analyzers/screening_coins_master.py

# Status del progetto
status:
	@echo "📋 Status del progetto:"
	@echo "----------------------"
	@if [ -f "config/api_keys.py" ]; then echo "✅ API Keys configurate"; else echo "❌ API Keys mancanti"; fi
	@if [ -f "data/inputs/idcoins" ]; then echo "✅ File idcoins presente"; else echo "❌ File idcoins mancante"; fi
	@if [ -d "venv" ]; then echo "✅ Ambiente virtuale presente"; else echo "❌ Ambiente virtuale mancante"; fi
	@if [ -n "$$(ls data/outputs/ 2>/dev/null)" ]; then echo "✅ Risultati presenti"; else echo "⚠️  Nessun risultato"; fi

# Esecuzione bot interattivo
run:
	@echo "🤖 Avvio bot interattivo..."
	python main.py

# Target per sviluppatori
dev-install:
	pip install -r requirements.txt
	pip install black flake8 isort pytest

# Backup configurazione
backup:
	@echo "💾 Backup configurazione..."
	mkdir -p backups
	cp -r config/ backups/config_$$(date +%Y%m%d_%H%M%S)/
	@echo "✅ Backup salvato in backups/"
