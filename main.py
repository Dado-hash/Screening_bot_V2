#!/usr/bin/env python3
"""
Cryptocurrency Screening Bot V2 - Main Entry Point

Questo script fornisce un'interfaccia unificata per tutte le funzionalità del bot.
"""

import sys
import os
from pathlib import Path

# Aggiungi la cartella src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import questionary
from colorama import init, Fore, Style

# Inizializza colorama per output colorato
init()

def print_banner():
    """Stampa il banner del programma."""
    banner = f"""
{Fore.CYAN}
╔══════════════════════════════════════════════════════════════╗
║                 CRYPTOCURRENCY SCREENING BOT V2             ║
║                        Dado-hash © 2024                     ║
╚══════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}
"""
    print(banner)

def check_dependencies():
    """Verifica che le dipendenze principali siano installate."""
    required_modules = [
        'pandas', 'numpy', 'pycoingecko', 'plotly', 
        'colorama', 'questionary', 'openpyxl'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"{Fore.RED}❌ Moduli mancanti: {', '.join(missing_modules)}")
        print(f"Installa con: pip install {' '.join(missing_modules)}{Style.RESET_ALL}")
        return False
    
    return True

def check_config():
    """Verifica che i file di configurazione esistano."""
    config_files = [
        "config/api_keys.py",
        "data/inputs/idcoins"
    ]
    
    missing_files = []
    for file_path in config_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"{Fore.YELLOW}⚠️  File di configurazione mancanti:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        
        if "config/api_keys.py" in missing_files:
            print(f"\n💡 Copia config/api_keys.py.example in config/api_keys.py")
            print(f"   e inserisci le tue API keys{Style.RESET_ALL}")
        
        return False
    
    return True

def run_data_fetcher():
    """Esegue il data fetcher."""
    print(f"\n{Fore.GREEN}🔄 Avvio raccolta dati...{Style.RESET_ALL}")
    
    source = questionary.select(
        "Quale fonte dati vuoi usare?",
        choices=[
            "CoinGecko (Consigliato)",
            "Binance",
            "Torna al menu principale"
        ]
    ).ask()
    
    if source == "CoinGecko (Consigliato)":
        try:
            from data_fetchers.get_historical_data_coingecko import main
            main()
        except ImportError as e:
            print(f"{Fore.RED}❌ Errore import: {e}{Style.RESET_ALL}")
    elif source == "Binance":
        try:
            from data_fetchers.get_historical_data_binance import main
            main()
        except ImportError as e:
            print(f"{Fore.RED}❌ Errore import: {e}{Style.RESET_ALL}")

def run_screening():
    """Esegue lo screening delle criptovalute."""
    print(f"\n{Fore.GREEN}📊 Avvio screening...{Style.RESET_ALL}")
    
    screen_type = questionary.select(
        "Quale tipo di screening vuoi eseguire?",
        choices=[
            "Screening Master (Principale)",
            "Screening 30 giorni CoinGecko",
            "Analisi Cumulativa",
            "Torna al menu principale"
        ]
    ).ask()
    
    if screen_type == "Screening Master (Principale)":
        try:
            import subprocess
            import sys
            subprocess.run([sys.executable, "src/analyzers/screening_coins_modern.py"])
        except Exception as e:
            print(f"{Fore.RED}❌ Errore screening: {e}{Style.RESET_ALL}")
    elif screen_type == "Screening 30 giorni CoinGecko":
        try:
            from analyzers.screening_coins_30d_coingecko import main
            main()
        except ImportError as e:
            print(f"{Fore.RED}❌ Errore import: {e}{Style.RESET_ALL}")
    elif screen_type == "Analisi Cumulativa":
        try:
            from analyzers.screening_coins_cumulatives import main
            main()
        except ImportError as e:
            print(f"{Fore.RED}❌ Errore import: {e}{Style.RESET_ALL}")

def run_analysis():
    """Esegue analisi avanzate."""
    print(f"\n{Fore.GREEN}🔍 Avvio analisi avanzate...{Style.RESET_ALL}")
    
    analysis_type = questionary.select(
        "Quale analisi vuoi eseguire?",
        choices=[
            "Analisi Volatilità",
            "Ricerca Top Annuali", 
            "Analisi Cicli 45m",
            "Torna al menu principale"
        ]
    ).ask()
    
    if analysis_type == "Analisi Volatilità":
        try:
            from analyzers.volatility import main
            main()
        except ImportError as e:
            print(f"{Fore.RED}❌ Errore import: {e}{Style.RESET_ALL}")
    elif analysis_type == "Ricerca Top Annuali":
        try:
            from analyzers.finding_annual_tops import main
            main()
        except ImportError as e:
            print(f"{Fore.RED}❌ Errore import: {e}{Style.RESET_ALL}")
    elif analysis_type == "Analisi Cicli 45m":
        try:
            from analyzers.finding_cycles_45m import main
            main()
        except ImportError as e:
            print(f"{Fore.RED}❌ Errore import: {e}{Style.RESET_ALL}")

def view_results():
    """Mostra i risultati delle analisi."""
    print(f"\n{Fore.BLUE}📈 Apertura cartella risultati...{Style.RESET_ALL}")
    
    results_path = "data/outputs"
    if os.path.exists(results_path):
        # Su macOS usa 'open', su Windows 'start', su Linux 'xdg-open'
        import platform
        system = platform.system()
        
        if system == "Darwin":  # macOS
            os.system(f"open {results_path}")
        elif system == "Windows":
            os.system(f"start {results_path}")
        else:  # Linux
            os.system(f"xdg-open {results_path}")
        
        print(f"📁 Cartella {results_path} aperta nel file manager")
    else:
        print(f"{Fore.YELLOW}⚠️  Cartella risultati non trovata: {results_path}{Style.RESET_ALL}")

def show_status():
    """Mostra lo stato del sistema."""
    print(f"\n{Fore.BLUE}📋 Status del Sistema{Style.RESET_ALL}")
    print("=" * 50)
    
    # Verifica dipendenze
    if check_dependencies():
        print(f"{Fore.GREEN}✅ Dipendenze: OK{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}❌ Dipendenze: MANCANTI{Style.RESET_ALL}")
    
    # Verifica configurazione
    if check_config():
        print(f"{Fore.GREEN}✅ Configurazione: OK{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}⚠️  Configurazione: INCOMPLETA{Style.RESET_ALL}")
    
    # Verifica dati
    if os.path.exists("data/outputs") and os.listdir("data/outputs"):
        print(f"{Fore.GREEN}✅ Dati: Risultati presenti{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}⚠️  Dati: Nessun risultato trovato{Style.RESET_ALL}")

def main():
    """Funzione principale."""
    print_banner()
    
    # Verifica prerequisiti
    if not check_dependencies():
        return
    
    while True:
        try:
            action = questionary.select(
                "Cosa vuoi fare?",
                choices=[
                    "🔄 Raccogliere Dati Storici",
                    "📊 Eseguire Screening",
                    "🔍 Analisi Avanzate",
                    "📈 Visualizzare Risultati",
                    "📋 Mostra Status Sistema",
                    "❓ Mostra Aiuto",
                    "🚪 Esci"
                ]
            ).ask()
            
            if action == "🔄 Raccogliere Dati Storici":
                run_data_fetcher()
            elif action == "📊 Eseguire Screening":
                run_screening()
            elif action == "🔍 Analisi Avanzate":
                run_analysis()
            elif action == "📈 Visualizzare Risultati":
                view_results()
            elif action == "📋 Mostra Status Sistema":
                show_status()
            elif action == "❓ Mostra Aiuto":
                show_help()
            elif action == "🚪 Esci":
                print(f"\n{Fore.GREEN}👋 Arrivederci!{Style.RESET_ALL}")
                break
            
            print("\n" + "="*60)
            
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}👋 Operazione interrotta dall'utente{Style.RESET_ALL}")
            break
        except Exception as e:
            print(f"\n{Fore.RED}❌ Errore inaspettato: {e}{Style.RESET_ALL}")

def show_help():
    """Mostra l'aiuto."""
    help_text = f"""
{Fore.BLUE}📚 GUIDA RAPIDA{Style.RESET_ALL}

{Fore.YELLOW}1. Workflow Consigliato:{Style.RESET_ALL}
   • Prima volta: Raccogliere Dati Storici
   • Poi: Eseguire Screening (2 volte: avanti e indietro)
   • Infine: Visualizzare Risultati

{Fore.YELLOW}2. File Importanti:{Style.RESET_ALL}
   • config/api_keys.py - Le tue API keys
   • data/inputs/idcoins - Lista criptovalute da analizzare
   • data/outputs/ - Risultati delle analisi

{Fore.YELLOW}3. Fogli Excel da Controllare:{Style.RESET_ALL}
   • cumulative_changes_forward.xlsx
   • cumulative_changes_backward.xlsx
   • leaderboard_forward.xlsx

{Fore.YELLOW}4. Supporto:{Style.RESET_ALL}
   • README.md - Documentazione completa
   • docs/ - Guide dettagliate
   • GitHub Issues - Segnalazione problemi

{Fore.GREEN}💡 Tip: Esegui sempre 'Mostra Status Sistema' per verificare la configurazione!{Style.RESET_ALL}
"""
    print(help_text)

if __name__ == "__main__":
    main()
