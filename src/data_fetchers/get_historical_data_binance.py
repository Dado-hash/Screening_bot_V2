from binance import Client
import api_keys
import pandas as pd
import colorama
import numpy as np
from datetime import timedelta

pd.options.mode.chained_assignment = None


def progress_bar(progress, total, color=colorama.Fore.YELLOW):
    percent = 100 * (progress / float(total))
    bar = '*' * int(percent) + '-' * (100 - int(percent))
    print(color + f"\r|{bar}| {percent:.2f}%", end="\r")
    if progress == total:
        print(colorama.Fore.GREEN + f"\r|{bar}| {percent:.2f}%", end="\r")
        print(colorama.Fore.RESET)

pd.set_option('display.float_format', lambda x: '%.10f' % x)

# getting coins from binance
list_symbols = []
client = Client(api_keys.API_KEY, api_keys.SECRET)
exchange_info = client.get_exchange_info()
for s in exchange_info['symbols']:
    if s["quoteAsset"] == 'BTC':
        list_symbols.append(s['symbol'])

# getting BTC data
date = input("Inserisci la data di partenza per lo storico (i.e. 1 Jan, 2023)\n")
klines = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_1DAY,
                                      date)  # "1 Dec, 2017", "1 Jan, 2018" per un intervallo

# reformatting some columns and 24h change
df_klines = pd.DataFrame(klines)
df_klines.columns = ['Open time', 'Open price', 'High price', 'Low price', 'Close price', 'Volume', 'Close time',
                     'trash1', 'trash2', 'trash3', 'trash4', 'trash5']

df_klines['Open time'] = pd.to_datetime(df_klines['Open time'].astype(float), unit='ms').dt.date
df_klines['Close time'] = pd.to_datetime(df_klines['Close time'].astype(float), unit='ms').dt.date
df_klines['24h change'] = (df_klines['Close price'].astype(float) - df_klines['Open price'].astype(float)) / df_klines[
    'Open price'].astype(float)

# calculating SMAs and if price is over these
df_klines['SMA_fast'] = df_klines['Close price'].rolling(5).mean()
df_klines['SMA_medium'] = df_klines['Close price'].rolling(10).mean()
df_klines['SMA_slow'] = df_klines['Close price'].rolling(60).mean()
df_klines['Above SMA_fast'] = np.where(df_klines['Close price'].astype(float) > df_klines['SMA_fast'], 3, -3)
df_klines['Above SMA_medium'] = np.where(df_klines['Close price'].astype(float) > df_klines['SMA_medium'], 2, -2)
df_klines['Above SMA_slow'] = np.where(df_klines['Close price'].astype(float) > df_klines['SMA_slow'], 1, -1)

df_klines.drop(['trash1', 'trash2', 'trash3', 'trash4', 'trash5'], axis=1, inplace=True)

# separating the columns to prepare them to be attached to those of the other coins
df_principal_highs = df_klines[['Close time', 'High price']]
df_principal_lows = df_klines[['Close time', 'Low price']]
df_principal_closes = df_klines[['Close time', 'Close price']]
df_principal_correlation = df_klines[['Close time', '24h change']]
df_principal_SMA_fast = df_klines[['Close time', 'SMA_fast']]
df_principal_SMA_medium = df_klines[['Close time', 'SMA_medium']]
df_principal_SMA_slow = df_klines[['Close time', 'SMA_slow']]
df_principal_above_fast = df_klines[['Close time', 'Above SMA_fast']]
df_principal_above_medium = df_klines[['Close time', 'Above SMA_medium']]
df_principal_above_slow = df_klines[['Close time', 'Above SMA_slow']]

df_principal_highs.columns = ['Close time', 'BTCUSD']
df_principal_lows.columns = ['Close time', 'BTCUSD']
df_principal_closes.columns = ['Close time', 'BTCUSD']
df_principal_correlation.columns = ['Close time', 'BTCUSD']
df_principal_SMA_fast.columns = ['Close time', 'BTCUSD']
df_principal_SMA_medium.columns = ['Close time', 'BTCUSD']
df_principal_SMA_slow.columns = ['Close time', 'BTCUSD']
df_principal_above_fast.columns = ['Close time', 'BTCUSD']
df_principal_above_medium.columns = ['Close time', 'BTCUSD']
df_principal_above_slow.columns = ['Close time', 'BTCUSD']

# repeating for all the remaining coins
count_bar = 0
for coin in list_symbols:

    klines = client.get_historical_klines(coin, Client.KLINE_INTERVAL_1DAY, "1 Set, 2022")
    df_klines = pd.DataFrame(klines)

    if len(df_klines.columns) == 12:
        df_klines.columns = ['Open time', 'Open price', 'High price', 'Low price', 'Close price', 'Volume',
                             'Close time', 'trash1', 'trash2', 'trash3', 'trash4', 'trash5']
        df_klines['Open time'] = pd.to_datetime(df_klines['Open time'].astype(float), unit='ms').dt.date
        df_klines['Close time'] = pd.to_datetime(df_klines['Close time'].astype(float), unit='ms').dt.date
        df_klines['24h change'] = (df_klines['Close price'].astype(float) - df_klines['Open price'].astype(float)) / \
                                  df_klines['Open price'].astype(float)
        df_klines['Correlation'] = df_klines['24h change'].astype(float) / df_principal_correlation['BTCUSD'].astype(
            float)

        df_klines['SMA_fast'] = df_klines['Close price'].rolling(6).mean()
        df_klines['SMA_medium'] = df_klines['Close price'].rolling(11).mean()
        df_klines['SMA_slow'] = df_klines['Close price'].rolling(21).mean()
        df_klines['Above SMA_fast'] = np.where(df_klines['Close price'].astype(float) > df_klines['SMA_fast'], 3, -3)
        df_klines['Above SMA_medium'] = np.where(df_klines['Close price'].astype(float) > df_klines['SMA_medium'], 2, -2)
        df_klines['Above SMA_slow'] = np.where(df_klines['Close price'].astype(float) > df_klines['SMA_slow'], 1, -1)

        df_klines.drop(['trash1', 'trash2', 'trash3', 'trash4', 'trash5'], axis=1, inplace=True)

        # separating the columns
        df_highs = df_klines[['Close time', 'High price']]
        df_lows = df_klines[['Close time', 'Low price']]
        df_closes = df_klines[['Close time', 'Close price']]
        df_correlation = df_klines[['Close time', 'Correlation']]
        df_SMA_fast = df_klines[['Close time', 'SMA_fast']]
        df_SMA_medium = df_klines[['Close time', 'SMA_medium']]
        df_SMA_slow = df_klines[['Close time', 'SMA_slow']]
        df_above_fast = df_klines[['Close time', 'Above SMA_fast']]
        df_above_medium = df_klines[['Close time', 'Above SMA_medium']]
        df_above_slow = df_klines[['Close time', 'Above SMA_slow']]

        # changing the name of the columns
        df_highs.columns = ['Close time', coin]
        df_lows.columns = ['Close time', coin]
        df_closes.columns = ['Close time', coin]
        df_correlation.columns = ['Close time', coin]
        df_SMA_fast.columns = ['Close time', coin]
        df_SMA_medium.columns = ['Close time', coin]
        df_SMA_slow.columns = ['Close time', coin]
        df_above_fast.columns = ['Close time', coin]
        df_above_medium.columns = ['Close time', coin]
        df_above_slow.columns = ['Close time', coin]

        # merging the data of the coin with those of all the others
        df_principal_highs = pd.merge(df_principal_highs, df_highs, on="Close time", how='left')
        df_principal_highs = df_principal_highs.copy()
        df_principal_lows = pd.merge(df_principal_lows, df_lows, on="Close time", how='left')
        df_principal_lows = df_principal_lows.copy()
        df_principal_closes = pd.merge(df_principal_closes, df_closes, on="Close time", how='left')
        df_principal_closes = df_principal_closes.copy()
        df_principal_correlation = pd.merge(df_principal_correlation, df_correlation, on="Close time", how='left')
        df_principal_correlation = df_principal_correlation.copy()
        df_principal_SMA_fast = pd.merge(df_principal_SMA_fast, df_SMA_fast, on="Close time", how='left')
        df_principal_SMA_fast = df_principal_SMA_fast.copy()
        df_principal_SMA_medium = pd.merge(df_principal_SMA_medium, df_SMA_medium, on="Close time", how='left')
        df_principal_SMA_medium = df_principal_SMA_medium.copy()
        df_principal_SMA_slow = pd.merge(df_principal_SMA_slow, df_SMA_slow, on="Close time", how='left')
        df_principal_SMA_slow = df_principal_SMA_slow.copy()
        df_principal_above_fast = pd.merge(df_principal_above_fast, df_above_fast, on="Close time", how='left')
        df_principal_above_fast = df_principal_above_fast.copy()
        df_principal_above_medium = pd.merge(df_principal_above_medium, df_above_medium, on="Close time", how='left')
        df_principal_above_medium = df_principal_above_medium.copy()
        df_principal_above_slow = pd.merge(df_principal_above_slow, df_above_slow, on="Close time", how='left')
        df_principal_above_slow = df_principal_above_slow.copy()

        count_bar += 1
        progress_bar(count_bar, len(list_symbols))

df_principal_highs.to_excel('highs.xlsx')
df_principal_lows.to_excel('lows.xlsx')
df_principal_closes.to_excel('closes.xlsx')
df_principal_correlation.to_excel('correlation.xlsx')
df_principal_SMA_fast.to_excel('SMA_fast.xlsx')
df_principal_SMA_medium.to_excel('SMA_medium.xlsx')
df_principal_SMA_slow.to_excel('SMA_slow.xlsx')
df_principal_above_fast.to_excel('above_fast.xlsx')
df_principal_above_medium.to_excel('above_medium.xlsx')
df_principal_above_slow.to_excel('above_slow.xlsx')

'''df_highs = df_principal_highs[['Close time', 'BTCUSD']]
df_lows = df_principal_lows[['Close time', 'BTCUSD']]
df_highs.columns = [['Close time', 'High price']]
df_lows.columns = [['Close time', 'Low price']]

# Tenkan sen
high_9 = df_highs['High price'].rolling(window=9).max()
low_9 = df_lows['Low price'].rolling(window=9).min()
print(high_9)
print(low_9)
print((high_9 + low_9) / 2)
df_highs['tenkan_sen'] = (high_9 + low_9) / 2
df_klines_temp = df_highs[['Close time', 'tenkan_sen']]

# Kijun sen
high_26 = df_highs['High price'].rolling(window=26).max()
low_26 = df_lows['Low price'].rolling(window=26).min()
df_klines_temp['kijun_sen'] = (high_26 + low_26) / 2

# this is to extend the 'df' in future for 26 days
# the 'df' here is numerical indexed df
last_index = df_klines_temp.iloc[-1:].index[0]
last_date = df_klines_temp['Close time'].iloc[-1]
for i in range(26):
    df_klines_temp.loc[last_index + 1 + i, 'Date'] = last_date + timedelta(days=i)

# Senkou span
df_klines_temp['senkou_span_a'] = ((df_klines_temp['tenkan_sen'] + df_klines_temp['kijun_sen']) / 2).shift(26)
high_52 = df_highs['High price'].rolling(window=52).max()
low_52 = df_lows['Low price'].rolling(window=52).min()
df_klines_temp['senkou_span_b'] = ((high_52 + low_52) / 2).shift(26)

# Chikou span
df_klines_temp['chikou_span'] = df_klines_temp['Close time'].shift(-22)

df_klines_temp_close = df_klines_temp['Close time']
df_klines_temp_data = df_klines_temp['Date']
df_klines_temp_close_result = df_klines_temp_close.combine_first(df_klines_temp_data)

df_klines_temp.drop(['High price', 'Low price', 'Close time', 'Date'], axis=1, inplace=True)
df_klines_temp = pd.concat([df_klines_temp, df_klines_temp_close_result], axis=1)

df_principal_tenkan = df_klines_temp[['Close time', 'tenkan_sen']]
df_principal_kijun = df_klines_temp[['Close time', 'kijun_sen']]
df_principal_senkou_a = df_klines_temp[['Close time', 'senkou_span_a']]
df_principal_senkou_b = df_klines_temp[['Close time', 'senkou_span_b']]
df_principal_chikou = df_klines_temp[['Close time', 'chikou_span']]

df_principal_tenkan.columns = ['Close time', 'BTCUSD']
df_principal_tenkan = df_principal_tenkan.dropna()
df_principal_kijun.columns = ['Close time', 'BTCUSD']
df_principal_kijun = df_principal_kijun.dropna()
df_principal_senkou_a.columns = ['Close time', 'BTCUSD']
df_principal_senkou_a = df_principal_senkou_a.dropna()
df_principal_senkou_b.columns = ['Close time', 'BTCUSD']
df_principal_senkou_b = df_principal_senkou_b.dropna()
df_principal_chikou.columns = ['Close time', 'BTCUSD']
df_principal_chikou = df_principal_chikou.dropna()

for coin in list_symbols:

    df_highs = df_principal_highs[['Close time', coin]]
    df_lows = df_principal_lows[['Close time', coin]]
    df_highs.columns = [['Close time', coin]]
    df_lows.columns = [['Close time', coin]]

    # Tenkan sen
    high_9 = df_highs['High price'].rolling(window=9).max()
    low_9 = df_lows['Low price'].rolling(window=9).min()
    df_highs['tenkan_sen'] = (high_9 + low_9) / 2
    df_klines_temp = df_highs[['Close time', 'tenkan_sen']]

    # Kijun sen
    high_26 = df_highs['High price'].rolling(window=26).max()
    low_26 = df_lows['Low price'].rolling(window=26).min()
    df_klines_temp['kijun_sen'] = (high_26 + low_26) / 2

    # this is to extend the 'df' in future for 26 days
    # the 'df' here is numerical indexed df
    last_index = df_klines_temp.iloc[-1:].index[0]
    last_date = df_klines_temp['Close time'].iloc[-1]
    for i in range(26):
        df_klines_temp.loc[last_index + 1 + i, 'Date'] = last_date + timedelta(days=i)

    # Senkou span
    df_klines_temp['senkou_span_a'] = ((df_klines_temp['tenkan_sen'] + df_klines_temp['kijun_sen']) / 2).shift(26)
    high_52 = df_highs['High price'].rolling(window=52).max()
    low_52 = df_lows['Low price'].rolling(window=52).min()
    df_klines_temp['senkou_span_b'] = ((high_52 + low_52) / 2).shift(26)

    # Chikou span
    df_klines_temp['chikou_span'] = df_klines_temp['Close time'].shift(-22)

    df_klines_temp_close = df_klines_temp['Close time']
    df_klines_temp_data = df_klines_temp['Date']
    df_klines_temp_close_result = df_klines_temp_close.combine_first(df_klines_temp_data)

    df_klines_temp.drop(['High price', 'Low price', 'Close time', 'Date'], axis=1, inplace=True)
    df_klines_temp = pd.concat([df_klines_temp, df_klines_temp_close_result], axis=1)

    df_tenkan = df_klines_temp[['Close time', 'tenkan_sen']]
    df_kijun = df_klines_temp[['Close time', 'kijun_sen']]
    df_senkou_a = df_klines_temp[['Close time', 'senkou_span_a']]
    df_senkou_b = df_klines_temp[['Close time', 'senkou_span_b']]
    df_chikou = df_klines_temp[['Close time', 'chikou_span']]

    df_tenkan.columns = ['Close time', coin]
    df_tenkan = df_tenkan.dropna()
    df_kijun.columns = ['Close time', coin]
    df_kijun = df_kijun.dropna()
    df_senkou_a.columns = ['Close time', coin]
    df_senkou_a = df_principal_senkou_a.dropna()
    df_senkou_b.columns = ['Close time', coin]
    df_senkou_b = df_principal_senkou_b.dropna()
    df_chikou.columns = ['Close time', coin]
    df_chikou = df_chikou.dropna()

    df_principal_tenkan = pd.merge(df_principal_tenkan, df_tenkan, on="Close time", how='left')
    df_principal_tenkan = df_principal_tenkan.copy()
    df_principal_kijun = pd.merge(df_principal_kijun, df_kijun, on="Close time", how='left')
    df_principal_kijun = df_principal_kijun.copy()
    df_principal_senkou_a = pd.merge(df_principal_senkou_a, df_senkou_a, on="Close time", how='left')
    df_principal_senkou_a = df_principal_senkou_a.copy()
    df_principal_senkou_b = pd.merge(df_principal_senkou_b, df_senkou_b, on="Close time", how='left')
    df_principal_senkou_b = df_principal_senkou_b.copy()
    df_principal_chikou = pd.merge(df_principal_chikou, df_chikou, on="Close time", how='left')
    df_principal_chikou = df_principal_chikou.copy()

    count_bar += 1
    progress_bar(count_bar, len(list_symbols) * 2)

df_principal_tenkan.to_excel('tenkan.xlsx')
df_principal_kijun.to_excel('kijun.xlsx')
df_principal_senkou_a.to_excel('senkou_a.xlsx')
df_principal_senkou_b.to_excel('senkou_b.xlsx')
df_principal_chikou.to_excel('chikou.xlsx')'''