import pandas as pd   #trasferito in screening_coins_master
import datetime as dt
import time as t
import plotly.graph_objects as go
from plotly.offline import plot
from pycoingecko import CoinGeckoAPI
import decimal

cg = CoinGeckoAPI()
cg.ping()
pd.set_option("display.precision", 8)
pd.set_option('display.float_format', lambda x: '%.5f' % x)

list_df = []
for num in range(2):
    if(num!=0):
        complexPriceRequest = cg.get_coins_markets(vs_currency = 'btc', order = 'market_cap_desc', per_page = 6, page = num, price_change_percentage = '24h')
        list_df.append(pd.DataFrame(complexPriceRequest))
df = pd.concat(list_df)
list_columns = ['id', 'name', 'current_price', 'market_cap', 'high_24h', 'low_24h', 'price_change_percentage_24h']
df = df[list_columns]   
df.set_index("id", inplace = True)
df.to_csv("idcoins")

list_df = []
for num in range(3):
    if(num>1):
        complexPriceRequest = cg.get_coins_markets(vs_currency = 'btc', order = 'market_cap_desc', per_page = 6, page = num, price_change_percentage = '24h')
        list_df.append(pd.DataFrame(complexPriceRequest))
df = pd.concat(list_df)
list_columns = ['id', 'name', 'current_price', 'market_cap', 'high_24h', 'low_24h', 'price_change_percentage_24h']
df = df[list_columns]   
df.set_index("id", inplace = True)
df.to_csv("idcoins1")

df = pd.read_csv("idcoins")
df1 = pd.read_csv("idcoins1")
coins_id_list = df["id"].tolist() + df1["id"].tolist()

#creo il file inizializzandolo con i dati di bitcoin
id_coin = 'bitcoin'
hist_data = cg.get_coin_ohlc_by_id(id = id_coin, vs_currency = 'usd', days = '30', interval = 'daily')
df = pd.DataFrame(hist_data)
df['day'] = df[[0]]
df['day'] = pd.to_datetime(df['day']/1000, unit = 's').dt.date
df['close'] = df[[4]]
df['open'] = df[[1]]
print(df)
df_with_first_row_per_day = df.groupby('day').first()
df_with_last_row_per_day = df.groupby('day').last()
df_giornaliero = df_with_last_row_per_day
df_giornaliero['24h_change'] = (df_with_last_row_per_day['close'] - df_with_first_row_per_day['open']) / df_with_first_row_per_day['open']
df['high'] = df[[2]]
df['low'] = df[[3]]
df_giornaliero['max_high'] = df.groupby(['day'], sort=False)['high'].max()
df_giornaliero['min_low'] = df.groupby(['day'], sort=False)['low'].min()
df_giornaliero['24h_volatility'] = (df_giornaliero['max_high'] - df_giornaliero['min_low']) / df_giornaliero['min_low']
df_giornaliero['correlation'] = df_giornaliero['24h_change'] / df_giornaliero['24h_change']
df_principale = df_giornaliero.drop(['close', 'open'], axis = 1, inplace = False)
df_principale = df_principale.drop([0, 1, 2, 3, 4], axis = 1, inplace = False)
columns = ['24h_change']
df_principale_24h = df_principale[columns]
columns = ['24h_volatility']
df_principale_volatility = df_principale[columns]
columns = ['correlation']
df_principale_correlation = df_principale[columns]
columns = ['max_high']
df_principale_high = df_principale[columns]
columns = ['min_low']
df_principale_low = df_principale[columns]
df_principale_24h.columns = [id_coin]
df_principale_volatility.columns = [id_coin]
df_principale_correlation.columns = [id_coin]
df_principale_low.columns = [id_coin]
df_principale_high.columns = [id_coin]

#aggiungo le alt
count = 0
i = 0
for id_coin in coins_id_list:
    if(id_coin != 'bitcoin'):
        if(count == 16):
            t.sleep(90)
            count = 0
        hist_data = cg.get_coin_ohlc_by_id(id = id_coin, vs_currency = 'btc', days = '30', interval = 'daily')
        df = pd.DataFrame(hist_data)
        df['day'] = df[[0]]
        df['day'] = pd.to_datetime(df['day']/1000, unit = 's').dt.date
        df['close'] = df[[4]]
        df['open'] = df[[1]]
        df_with_first_row_per_day = df.groupby('day').first()
        df_with_last_row_per_day = df.groupby('day').last()
        df_giornaliero = df_with_last_row_per_day
        df_giornaliero['24h_change'] = (df_with_last_row_per_day['close'] - df_with_first_row_per_day['open']) / df_with_first_row_per_day['open'] # - df_principale_24h['bitcoin']
        df['high'] = df[[2]]
        df['low'] = df[[3]]
        df_giornaliero['max_high'] = df.groupby(['day'], sort=False)['high'].max()
        df_giornaliero['min_low'] = df.groupby(['day'], sort=False)['low'].min()
        #dividere max e min per i max e min di Bitcoin
        df_giornaliero['24h_volatility'] = (df_giornaliero['max_high'] - df_giornaliero['min_low']) / df_giornaliero['min_low']
        df_giornaliero['correlation'] = df_giornaliero['24h_change'] / df_principale_24h['bitcoin']
        df_principale = df_giornaliero.drop(['close', 'open'], axis = 1, inplace = False)
        df_principale = df_principale.drop([0, 1, 2, 3, 4], axis = 1, inplace = False)
        columns = ['24h_change']
        df_24h = df_principale[columns]
        df_24h.columns = [id_coin]
        columns = ['24h_volatility']
        df_volatility = df_principale[columns]
        df_volatility.columns = [id_coin]
        columns = ['correlation']
        df_correlation = df_principale[columns]
        df_correlation.columns = [id_coin]
        columns = ['max_high']
        df_high = df_principale[columns]
        df_high.columns = [id_coin]
        columns = ['min_low']
        df_low = df_principale[columns]
        df_low.columns = [id_coin]
        df_principale_24h = pd.concat([df_principale_24h, df_24h], axis = 1)
        df_principale_volatility = pd.concat([df_principale_volatility, df_volatility], axis = 1)
        df_principale_correlation = pd.concat([df_principale_correlation, df_correlation], axis = 1)
        df_principale_low = pd.concat([df_principale_low, df_low], axis = 1)
        df_principale_high = pd.concat([df_principale_high, df_high], axis = 1)
        count += 1
        i += 1
        print(i)

#salvo i tre file con 24h_change e correlation
df_24h = df_principale_24h
df_principale_24h = df_principale_24h.T
df_principale_24h['sum'] = df_principale_24h.sum(axis = 1)
df_principale_24h = df_principale_24h.sort_values('sum', ascending = False)
df_principale_correlation.to_excel('correlation.xlsx')
df_principale_high.to_excel('high.xlsx')
df_principale_low.to_excel('low.xlsx')

'''leaderboard = []
for num in range(2, df_24h.shape[0] + 1):
    df_24h_sum = df_24h.iloc[(31-num) : 31].sum()
    df_24h_sum = df_24h_sum.sort_values(ascending = False)
    df_24h_sum = df_24h_sum.to_frame()
    df = df_24h_sum.copy()[[]]
    df_24h_sum.columns = ['Cumulative']
    df_24h_sum.reset_index(drop=True, inplace = True)
    ranking = pd.DataFrame(range(1, 1 + len(df_24h_sum)))
    ranking.columns = ['Rank']
    ranking['Cumulative'] = df_24h_sum['Cumulative']
    df_24h_sum = pd.concat([df_24h_sum, ranking], axis = 1)
    df_24h_sum.columns = ['Cumulative', 'Rank', 'Trash']
    df_24h_sum.drop('Trash', axis = 1, inplace = True)
    df_24h_sum.index = df.index
    leaderboard.append(df_24h_sum)
with pd.ExcelWriter('leaderboards.xlsx') as writer:  
    df_principale_24h.to_excel(writer, sheet_name = '24h_change')
    counter = 1
    for df in leaderboard:
        df.to_excel(writer, sheet_name = str(counter) + 'd')
        counter += 1'''

'''first = pd.read_excel('leaderboards.xlsx', sheet_name = '1d')
first.columns = ['Coin', 'Cumulative', 'Rank']
first.drop('Rank', inplace = True, axis = 1)
first.set_index('Coin', inplace = True)
df_principale_24h = pd.read_excel('leaderboards.xlsx', sheet_name = '24h_change')'''

'''leaderboard = []
for num in range(1, 30):
    first_df = pd.read_excel('leaderboards.xlsx', sheet_name = str(num) + 'd')
    second_df = pd.read_excel('leaderboards.xlsx', sheet_name = str(num+1) + 'd')
    first_df.columns = ['Coin', 'Cumulative', 'Rank1']
    second_df.columns = ['Coin', 'Cumulative', 'Rank2']
    first_df.drop('Cumulative', inplace = True, axis = 1)
    df = second_df.merge(first_df, on = 'Coin')
    df['Change'] = df['Rank1'] - df['Rank2']
    df.drop(['Rank1', 'Rank2'], inplace = True, axis = 1)
    df.set_index('Coin', inplace = True)
    leaderboard.append(df)

with pd.ExcelWriter('leaderboards.xlsx') as writer:  
    df_principale_24h.to_excel(writer, sheet_name = '24h_change')
    counter = 1
    for df in leaderboard:
        if(counter == 1):
            first.to_excel(writer, sheet_name = '1d')
            counter += 1
        else:
            df.to_excel(writer, sheet_name = str(counter) + 'd')
            counter += 1'''