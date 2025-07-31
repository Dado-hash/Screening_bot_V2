from http import client
from tkinter.filedialog import Open
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
import pandas as pd
import api_keys
import mplfinance as mpf
import numpy as np

client = Client(api_keys.API_KEY, api_keys.SECRET)

#prendere tutti i tickers da binance
tickers = client.get_all_tickers()
print(tickers)

#dalla lista prendo il primo e prendo solo il prezzo
tickers[0]['price']

tickers_df = pd.DataFrame(tickers)

#prendo i primi n
tickers_df.head()

#prendo gli ultimi n
tickers_df.tail()

#scelgo che parametro usare per indicizzare la lista
tickers_df.set_index('symbol', inplace = True) 

#prendo un valore usando l'indice (float(...) per convertire)
tickers_df.loc('BTCUSDT')

#restituisce i tipi che compongono il dataset
tickers_df.dtypes

#ottenere i dati storici
historical = client.get_historical_klines('ETHBTC', Client.KLINE_INTERVAL_1DAY, '1 Jan 2020')
#VALORI:
#Open Time
#Open
#High
#Low
#Close
#Volume
#Close Time
#Quote Asset Volume
#Number Of Trades
#Taker Buy Base Asset Volume
#Taker Buy Quote Asset Volume
#Ignore

hist_df = pd.DataFrame(historical)

#rinominare le colonne
hist_df.columns = ['Open Time', 'Open', 'Close', ...]

#dimenisoni dataset
hist_df.shape

#per convertire in data
hist_df['Open Time'] = pd.to_datetime(hist_df['Open Time']/1000, unit = 's')

#per converirne di più in una volta sola
numeric_columns = ['Open', 'High', 'Low', 'Close', ...]
hist_df[numeric_columns] = hist_df[numeric_columns].apply(pd.to_numeric, axis = 1)

#avere alcune statistiche (solo se sono dati numerici)
hist_df.describe()

#avere alcune statistiche (se sono object)
hist_df.describe(include = 'object')

#informazioni addizionali
hist_df.info()

#creare un grafico
mpf.plot(hist_df.set_index('Close Time').tail(100), type = 'candle', style = 'charles', volume = True, title = 'ETHBTC Last 100 Days', mav = (10,20,30))

#creare un dataset da un file csv
df = pd.read_csv('[nome file]')

#creare un dataset da un file csv indicizzandolo
pd.read_csv('[nome file]', index_col='nome colonna che indicizza')

#filtrare tra colonne
df.State
df['International Plan']    #se ci sono spazi nel nome
df['State', 'International Plan']
df.State.unique()           #restituisce i valori unici in una certa colonna

#filtrare tra righe
df[df['International Plan'] == 'No']        #prendo solo le righe che hanno 'No' nella colonna di 'International Plan'
df[(df['International Plan'] == 'No') & (df['Churn'] == True)]

#prendere una determinata riga
df.iloc[14]
df.iloc[[14]]               #per stampare in orizzontale
df.iloc[22:33]              #dalla riga 22 alla 33

#prendere un valore dati riga e colonna
df.iloc[14, 0]
df.iloc[14, -1]             #prende il valore da destra

#cancellare righe
df.isnull().sum             #conta quante righe sono null
df.dropna(inplace = True)   #cancella le righe nulle

#cancellare colonne
df.drop('Area Code', axis = 1)   
new_df = df['lista delle colonne che voglio tenere']   

#aggiungere colonne
df['New Column'] = df['Column'] + df['Column_2']

#aggiornare un'intera colonna
df['New Column'] = 100

#aggiornare un singolo valore
df.iloc[0, -1] = 10

#aggiornare secondo una condizione
df['Churn'] = df['Churn'].apply(lambda x: 1 if x == True else 0)

#creare un csv
df.to_csv('output.csv')

#ciclare sulle colonne del df
for c in df.columns:
    print(c)

#creare una lista con i nomi delle colonne
list(df.columns)

#riordinare le colonne
df.reindex(columns='lista con i nomi delle colonne riordinati')

#creare lista nomi colonne
data_cols = ['id', 'date', ...]

#eliminare un carattere nei valori di una colonna
new_df['price'] = new_df['price'].str.replace(r'carattere da cancellare', 'carattere che sostituisce').astype('tipo in cui riconvertire')

#concatenare piu' data frame
pd.concat(['nome df1', 'nome df2'])

#restituire il numero di righe di un data frame
len(df.index)

#creare una pivot table
pd.pivot_table('nome df', index=['nome indice con cui raggruppare (anche piu di uno)'], values='valori da raggruppare (anche piu di uno)', agfunc=np.'funzione con cui raggruppare')

#mergiare due data frame
df.merge('nome df da mergiare', how='che tipo di join(destro, sinistro, inner, outer', on='cosa usare per matchare')