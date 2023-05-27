import pandas as pd
import psycopg2
from datetime import datetime
import requests
import time
import sys

def get_cryptos_binance():
    # URL base delle API di Binance
    base_url = 'https://api.binance.com'

    # Endpoint per ottenere l'elenco di tutte le coppie di trading
    endpoint = '/api/v3/exchangeInfo'

    # Invia la richiesta alle API di Binance
    response = requests.get(base_url + endpoint)

    # Estrae le coppie di trading che includono Bitcoin
    data = response.json()
    btc_pairs = [symbol['symbol'] for symbol in data['symbols'] if 'BTC' in symbol['symbol']]

    # Salva la lista delle coppie di trading in cryptos
    cryptos = list(set([pair.split('BTC')[0] for pair in btc_pairs]))

    return cryptos

# Connessione al database Postgres
conn = psycopg2.connect(host='localhost', database='screeningbot', user='postgres', password='dev_password')

# Definizione della funzione che scarica i dati storici di una criptovaluta da Coingecko
def get_historical_data(crypto):
    base_url = 'https://api.binance.com'
    endpoint = '/api/v3/klines'
    response = requests.get(base_url + endpoint, params={
        'symbol': crypto + 'BTC',
        'interval': '1d'
    })
    data = response.json()
    df = pd.DataFrame(data, columns=['timestamp_open', 'open_price', 'high_price', 'low_price', 'close_price', 'volume', 'timestamp_close', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    df['timestamp_open'] = df['timestamp_open'].apply(lambda x: datetime.fromtimestamp(x/1000).strftime('%Y-%m-%d'))
    df['timestamp_close'] = df['timestamp_close'].apply(lambda x: datetime.fromtimestamp(x/1000).strftime('%Y-%m-%d'))
    df.drop(columns=['quote_asset_volume', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'], inplace=True)
    return df

def table_exists(crypto):
    crypto = crypto.lower()
    cur = conn.cursor()
    cur.execute(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'historical_data_{crypto}')")
    exists = cur.fetchone()[0]
    return exists

def create_table(crypto):
    cur = conn.cursor()
    cur.execute(f"""
        CREATE TABLE historical_data_{crypto} (
            id SERIAL PRIMARY KEY,
            timestamp_open DATE NOT NULL,
            open_price NUMERIC(20, 10) NOT NULL,
            high_price NUMERIC(20, 10) NOT NULL,
            low_price NUMERIC(20, 10) NOT NULL,
            close_price NUMERIC(20, 10) NOT NULL,
            volume NUMERIC(30, 15) NOT NULL,
            timestamp_close DATE NOT NULL,
            number_of_trades NUMERIC(20, 10) NOT NULL,
            ma5 NUMERIC(20, 10),
            ma10 NUMERIC(20, 10),
            ma60 NUMERIC(20, 10),
            ma223 NUMERIC(20, 10)
        )
    """)
    conn.commit()

# Definizione della funzione che inserisce i dati storici di una criptovaluta nel database Postgres
def insert_data(crypto):
    if not table_exists(crypto):
        create_table(crypto)
        df = get_historical_data(crypto)
        cur = conn.cursor()
        for _, row in df.iterrows():
            try:
                cur.execute(f"INSERT INTO historical_data_{crypto} (timestamp_open , open_price, high_price, low_price, close_price, volume, timestamp_close, number_of_trades) VALUES ('{row['timestamp_open']}', {row['open_price']}, {row['high_price']}, {row['low_price']}, {row['close_price']}, {row['volume']}, '{row['timestamp_close']}', {row['number_of_trades']})")
                conn.commit()
            except Exception as e:
                print(f"Errore nell'inserimento del seguente dato: {row}")
                print(f"Errore: {e}")
    else:
        df = get_historical_data(crypto)
        cur = conn.cursor()
        for _, row in df.iterrows():
            cur.execute(f"SELECT id FROM historical_data_{crypto} WHERE timestamp_open = '{row['timestamp_open']}'")
            res = cur.fetchone()
            if res is None:
                try:
                    cur.execute(f"INSERT INTO historical_data_{crypto} (timestamp_open , open_price, high_price, low_price, close_price, volume, timestamp_close, number_of_trades) VALUES ('{row['timestamp_open']}', {row['open_price']}, {row['high_price']}, {row['low_price']}, {row['close_price']}, {row['volume']}, '{row['timestamp_close']}', {row['number_of_trades']})")
                    conn.commit()
                except Exception as e:
                    print(f"Errore nell'inserimento del seguente dato: {row}")
                    print(f"Errore: {e}")
            else:
                try:
                    cur.execute(f"UPDATE historical_data_{crypto} SET open_price = {row['open_price']}, high_price = {row['high_price']}, low_price = {row['low_price']}, close_price = {row['close_price']}, volume = {row['volume']}, timestamp_close = '{row['timestamp_close']}', number_of_trades = {row['number_of_trades']} WHERE timestamp_open = '{row['timestamp_open']}'")
                    conn.commit()
                except Exception as e:
                    print(f"Errore nell'aggiornamento del seguente dato: {row}")
                    print(f"Errore: {e}")

def calculate_emas(crypto):
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM historical_data_{crypto}")

    # Creazione di un DataFrame pandas con i dati estratti dal database
    df = pd.DataFrame(cur.fetchall(),
                      columns=['id', 'timestamp_open', 'open_price', 'high_price', 'low_price', 'close_price', 'volume',
                               'timestamp_close', 'number_of_trades', 'ma5', 'ma10', 'ma60', 'ma223'])

    # Calcolo della media mobile a 5 giorni
    df['ma5'] = df['close_price'].rolling(window=5).mean().fillna(value=0)
    # Calcolo della media mobile a 10 giorni
    df['ma10'] = df['close_price'].rolling(window=10).mean().fillna(value=0)
    # Calcolo della media mobile a 60 giorni
    df['ma60'] = df['close_price'].rolling(window=60).mean().fillna(value=0)
    # Calcolo della media mobile a 223 giorni
    df['ma223'] = df['close_price'].rolling(window=223).mean().fillna(value=0)

    # Inserimento dei valori della media mobile nella tabella
    for index, row in df.iterrows():
        cur.execute(f"UPDATE historical_data_{crypto} SET ma5 = {row['ma5']}, ma10 = {row['ma10']}, ma60 = {row['ma60']}, ma223 = {row['ma223']} WHERE timestamp_open = '{row['timestamp_open']}'")

# Definizione della funzione che aggiorna la barra di avanzamento
def update_progress_bar(progress, bar_length=100):
    sys.stdout.write('\rElaborazione: ')
    # crea la barra di avanzamento
    bar = '['
    for i in range(bar_length):
        if i < int(progress * bar_length):
            bar += '*'
        else:
            bar += ' '
    bar += ']'
    # stampa la barra di avanzamento e il progresso
    sys.stdout.write(bar + ' ' + str(int(progress * 100.0)) + '%')
    sys.stdout.flush()

# Iterazione sulla lista delle criptovalute di interesse e inserimento dei dati storici nel database Postgres
cryptos = get_cryptos_binance()
total_cryptos = len(cryptos)
count = 0
for crypto in cryptos:
    if crypto != '':
        insert_data(crypto)
        calculate_emas(crypto)
    count += 1
    # aggiorna la barra di avanzamento ogni volta che si elabora una criptovaluta
    progress = count / float(total_cryptos)
    update_progress_bar(progress)

# Chiusura della connessione al database Postgres
conn.close()
