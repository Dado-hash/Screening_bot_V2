import pandas as pd
import numpy as np
import csv

pd.set_option('display.float_format', lambda x: '%.15f' % x)
pd.options.mode.chained_assignment = None

periods = input("Inserisci il numero di giorni su cui vuoi calcolare la volatilità -> ")
periods = periods.split()
for i in range(len(periods)):
    periods[i] = int(periods[i])

highs = pd.read_excel('highs.xlsx', index_col=0, engine='openpyxl')
lows = pd.read_excel('lows.xlsx', index_col=0, engine='openpyxl')
closes = pd.read_excel('closes.xlsx', index_col=0, engine='openpyxl')

coins = highs.columns

for y, count in enumerate(periods):
    dict_val = {}
    for i, val in enumerate(coins):
        if val != 'Close time':
            df_temp = highs[['Close time', val]]
            df_temp.columns = ['Close time', 'high']
            df_temp['low'] = lows[val]
            df_temp['closes'] = closes[val]
            df_temp = df_temp.tail(count)
            last_closes = df_temp['closes'].tolist()
            mean = sum(last_closes) / count
            df_temp['waste high'] = np.where(df_temp['high'] - mean >= 0,
                                             (df_temp['high'] - mean) / mean,
                                             (df_temp['high'] - mean) / df_temp['high'] * (-1))
            df_temp['waste low'] = np.where(df_temp['low'] - mean >= 0,
                                            (df_temp['low'] - mean) / mean,
                                            (df_temp['low'] - mean) / df_temp['low'] * (-1))
            df_temp['waste'] = np.where(df_temp['waste high'] >= df_temp['waste low'], df_temp['waste high'],
                                        df_temp['waste low'])
            df_temp.drop(['waste high', 'waste low'], inplace=True, axis=1)
            df_temp['waste'] = df_temp['waste'] ** 2
            waste = df_temp['waste'].tolist()
            standard_deviation = (sum(waste) / count) ** (1 / 2) * 100
            dict_val[val] = standard_deviation
    df_sd = pd.Series(dict_val, name='Standard deviation')
    df_sd.to_excel('volatility_' + str(count) + '.xlsx')
