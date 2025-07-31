import pandas as pd
import datetime as dt
import time as t
import plotly.graph_objects as go
from plotly.offline import plot
from pycoingecko import CoinGeckoAPI

cg = CoinGeckoAPI()

cg.ping()

#prendo l'id delle prime 1000 coin per market cap
list_df = []
for num in range(6):
    if(num!=0):
        complexPriceRequest = cg.get_coins_markets(vs_currency = 'btc', order = 'market_cap_desc', per_page = 100, page = num, price_change_percentage = '24h')
        list_df.append(pd.DataFrame(complexPriceRequest))
df = pd.concat(list_df)
list_columns = ['id', 'name', 'current_price', 'market_cap', 'high_24h', 'low_24h', 'price_change_percentage_24h']
df = df[list_columns]   
df.set_index("id", inplace = True)
df.to_csv("idcoins")

list_df = []
for num in range(11):
    if(num>5):
        complexPriceRequest = cg.get_coins_markets(vs_currency = 'btc', order = 'market_cap_desc', per_page = 100, page = num, price_change_percentage = '24h')
        list_df.append(pd.DataFrame(complexPriceRequest))
df = pd.concat(list_df)
list_columns = ['id', 'name', 'current_price', 'market_cap', 'high_24h', 'low_24h', 'price_change_percentage_24h']
df = df[list_columns]   
df.set_index("id", inplace = True)
df.to_csv("idcoins1")

df = pd.read_csv("idcoins")
df1 = pd.read_csv("idcoins1")
coins_id_list = df["id"].tolist() + df1["id"].tolist()

#creo il file mettendo i prezzi di bitcoin
id_coin = 'bitcoin'
hist_data = cg.get_coin_market_chart_by_id(id = id_coin, vs_currency = 'usd', days = 'max', interval = 'daily')
df = pd.DataFrame(hist_data)
df.drop(df.tail(1).index,inplace=True)
df['day'] = df['prices'].str[0]
df['day'] = pd.to_datetime(df['day']/1000, unit = 's').dt.date
df[id_coin] = df['prices'].str[1].astype(str)
df[id_coin] = df[id_coin].str.replace(r'.', ',')
print(df.dtypes)
columns = ['day', id_coin]
df_principale = df[columns]
df_principale.set_index('day', inplace = True)
print(df_principale)

#aggiungo le alt
count = 0
for id_coin in coins_id_list:
    if(id_coin != 'bitcoin'):
        if(count == 30):
            t.sleep(80)
            count = 0
        hist_data = cg.get_coin_market_chart_by_id(id = id_coin, vs_currency = 'usd', days = 'max', interval = 'daily')
        df = pd.DataFrame(hist_data)
        df.drop(df.tail(1).index,inplace=True)
        df['day'] = df['prices'].str[0]
        df['day'] = pd.to_datetime(df['day']/1000, unit = 's').dt.date
        df[id_coin] = df['prices'].str[1].astype(str)
        df[id_coin] = df[id_coin].str.replace(r'.', ',')
        columns = ['day', id_coin]
        df = df[columns]
        df.set_index('day', inplace = True)
        df_principale = pd.merge(df_principale, df, on="day", how = 'left')
        count += 1
        print(df_principale)
        
#salvo lo storico
df_principale.to_csv('storico.csv')