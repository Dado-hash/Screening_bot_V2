import pandas as pd
import psycopg2
import sys

# Connessione al database Postgres
conn = psycopg2.connect(host='localhost', database='screeningbot', user='postgres', password='dev_password')

def calculate_cumulative_performance(n_days):
    cur = conn.cursor()
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    tables = cur.fetchall()

    total_tables = len(tables)
    count = 0

    for table in tables:
        crypto = table[0].replace('historical_data_', '')
        cur.execute(f"SELECT timestamp_open, close_price, open_price FROM {table[0]} ORDER BY timestamp_open DESC LIMIT {n_days}")
        data = cur.fetchall()
        df = pd.DataFrame(data, columns=['timestamp', 'close_price', 'open_price'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['performance'] = (df['close_price'] - df['open_price']) / df['open_price'] * 100
        df['cumulative_performance'] = df['performance'][::-1].cumsum()[::-1]
        df.set_index('timestamp', inplace=True)
        df.dropna(inplace=True)

        # Creazione della tabella nel database per salvare i risultati
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS cumulative_performance_{crypto} (
                date DATE PRIMARY KEY,
                performance NUMERIC(10, 4) NOT NULL,
                cumulative_performance NUMERIC(10, 4) NOT NULL
            )
        """)
        conn.commit()

        # Inserimento dei dati nella tabella
        for index, row in df.iterrows():
            cur.execute(f"INSERT INTO cumulative_performance_{crypto} (date, performance, cumulative_performance) VALUES ('{index.strftime('%Y-%m-%d')}', {row['performance']}, {row['cumulative_performance']})")
            conn.commit()

        count += 1
        progress = count / float(total_tables)
        update_progress_bar(progress)

    print("\nCalcolo delle performance cumulative completato.")

# Funzione per chiedere all'utente il numero di giorni
def get_user_input():
    while True:
        try:
            n_days = int(input("Inserisci il numero di giorni per il calcolo della performance cumulativa: "))
            if n_days <= 0:
                print("Il numero di giorni deve essere un numero positivo.")
            else:
                return n_days
        except ValueError:
            print("Inserisci un numero valido.")

# Funzione per aggiornare la barra di avanzamento
def update_progress_bar(progress, bar_length=50):
    sys.stdout.write('\rProgresso: ')
    bar = '['
    for i in range(bar_length):
        if i < int(progress * bar_length):
            bar += '*'
        else:
            bar += ' '
    bar += ']'
    sys.stdout.write(bar + ' ' + str(int(progress * 100.0)) + '%')
    sys.stdout.flush()

def delete_cumulative_performance_tables():
    cur = conn.cursor()
    cur.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE 'cumulative_performance%'")
    tables = cur.fetchall()

    for table in tables:
        cur.execute(f"DROP TABLE IF EXISTS {table[0]}")
        conn.commit()

    print("Tabelle cumulative_performance eliminate.")

# Chiamata alla funzione per eliminare le tabelle cumulative_performance esistenti
delete_cumulative_performance_tables()

n_days = get_user_input()
calculate_cumulative_performance(n_days)

# Chiusura della connessione al database Postgres
conn.close()
