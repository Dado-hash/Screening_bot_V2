#!/bin/bash

# Setup script per Cryptocurrency Screening Bot V2
# Uso: ./setup.sh

set -e  # Exit on any error

echo "🚀 Cryptocurrency Screening Bot V2 - Setup"
echo "=========================================="

# Controllo versione Python
echo "🐍 Controllo versione Python..."
python_version=$(python3 --version 2>&1 | cut -d" " -f2 | cut -d"." -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo "✅ Python $python_version OK"
else
    echo "❌ Python $required_version o superiore richiesto. Trovato: $python_version"
    exit 1
fi

# Creazione ambiente virtuale
echo "📦 Creazione ambiente virtuale..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Ambiente virtuale creato"
else
    echo "ℹ️  Ambiente virtuale già esistente"
fi

# Attivazione ambiente virtuale
echo "🔌 Attivazione ambiente virtuale..."
source venv/bin/activate

# Aggiornamento pip
echo "⬆️  Aggiornamento pip..."
pip install --upgrade pip

# Installazione dipendenze
echo "📚 Installazione dipendenze..."
pip install -r requirements.txt

# Creazione cartelle necessarie
echo "📁 Creazione cartelle..."
mkdir -p data/outputs
mkdir -p data/inputs
mkdir -p cache
mkdir -p logs

# Setup file di configurazione
echo "⚙️  Setup configurazione..."
if [ ! -f "config/api_keys.py" ]; then
    cp config/api_keys.py.example config/api_keys.py
    echo "📝 File config/api_keys.py creato da template"
    echo "⚠️  IMPORTANTE: Modifica config/api_keys.py con le tue API keys!"
else
    echo "ℹ️  File config/api_keys.py già esistente"
fi

# Controllo file idcoins
if [ ! -f "data/inputs/idcoins" ]; then
    echo "⚠️  File data/inputs/idcoins non trovato"
    echo "💡 Crea questo file con la lista degli ID delle criptovalute da analizzare"
    echo "   Esempio contenuto:"
    echo "   bitcoin"
    echo "   ethereum"
    echo "   binancecoin"
fi

# Test import
echo "🧪 Test importazioni..."
python3 -c "
import pandas as pd
import numpy as np
import colorama
import questionary
print('✅ Moduli principali importati correttamente')
"

echo ""
echo "🎉 Setup completato!"
echo ""
echo "📋 Prossimi passi:"
echo "1. Modifica config/api_keys.py con le tue API keys"
echo "2. Crea/verifica data/inputs/idcoins con gli ID delle crypto"
echo "3. Attiva l'ambiente virtuale: source venv/bin/activate"
echo "4. Esegui il bot: python main.py"
echo ""
echo "📚 Per maggiori informazioni: cat README.md"
