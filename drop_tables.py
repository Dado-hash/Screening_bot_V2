import psycopg2

# Description: This script drops all tables in the database.
conn = psycopg2.connect(host='localhost', database='screeningbot', user='postgres', password='dev_password')

cur = conn.cursor()
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE';")
tables = cur.fetchall()

for table in tables:
    cur.execute(f"DROP TABLE IF EXISTS {table[0]} CASCADE;")

conn.commit()