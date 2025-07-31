from turtle import right
from binance import Client
import api_keys
import pandas as pd
from datetime import datetime, timedelta
import csv

client = Client(api_keys.API_KEY, api_keys.SECRET)
klines = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_15MINUTE, "1 Sep, 2022")
klines = pd.DataFrame(klines)
klines.columns = ['Open time', 'Open price', 'High price', 'Low price', 'Close price', 'Volume', 'Close time', 'Trash', 'Trades', 'Trash2', 'Trash3', 'Trash4']
klines.drop(['Trash', 'Trash2', 'Trash3', 'Trash4'], axis = 1, inplace = True)
klines['Open time'] = klines['Open time'].astype(float)
klines['Open time'] = klines['Open time']*1000000 
klines['Open time'] = pd.to_datetime(klines['Open time'])
klines['Close time'] = klines['Close time'].astype(float)
klines['Close time'] = klines['Close time']*1000000 
klines['Close time'] = pd.to_datetime(klines['Close time'])

klines_grouped_principale = klines.iloc[0:3]
klines_grouped_principale['group'] = 0
count = 1
for num in range(1, len(klines)//3):
    klines_grouped = klines.iloc[num*3:(num+1)*3]    
    klines_grouped['group'] = count
    klines_grouped_principale = pd.concat([klines_grouped_principale, klines_grouped])
    count += 1
if(count*3 < len(klines)):
    missing = len(klines) - count*3
    klines_grouped = klines.iloc[-missing:]
    klines_grouped['group'] = count
    klines_grouped_principale = pd.concat([klines_grouped_principale, klines_grouped])

df_with_first_row = klines_grouped_principale.groupby('group').first()
df_with_last_row = klines_grouped_principale.groupby('group').last()
df_45m = df_with_first_row[['Open time', 'Trades']]
df_45m['Open price'] = df_with_first_row['Open price']
df_45m['Close price'] = df_with_last_row['Close price']
df_45m.drop('Trades', axis = 1, inplace = True)
df_45m['High price'] = klines_grouped_principale.groupby(['group'], sort=False)['High price'].max()
df_45m['Low price'] = klines_grouped_principale.groupby(['group'], sort=False)['Low price'].min()
df_45m['Change'] = (df_45m['Close price'].astype(float) - df_45m['Open price'].astype(float)) / df_45m['Open price'].astype(float)

df_ultimate_dict = dict(zip(df_45m['Open time'], df_45m['Low price']))

min_date = str(input('Inserisci data e ora di un minimo (yyyy-mm-dd hh:mm:ss): '))
min_date = datetime.strptime(min_date, "%Y-%m-%d %H:%M:%S")

for k in list(df_ultimate_dict.keys()):
     if k < min_date:
        del df_ultimate_dict[k]

max_lenght = 44
min_lenght = 24
start = 6
end = 3

file = open('45m min.csv', 'w')
writer = csv.writer(file)
list_days = ['Candela in cui è avvenuto il minimo']
list_min = ['Prezzo raggiunto durante il minimo']
list_costraints = ['Candela in cui si è vincolato al rialzo']
list_price_costraints = ['Prezzo con il quale si è vincolato al rialzo']





while(min_date <= df_ultimate.tail(1).index):                                               
    left = df_ultimate.index.get_loc(min_date + timedelta(minutes=45*min_lenght))
    right = df_ultimate.index.get_loc(min_date + timedelta(minutes=45*max_lenght))

    next_min = df_ultimate.index[df_ultimate['Low price'] == df_ultimate.iloc[left:right]['Low price'].min()]
    if(len(next_min)>1):
        next_min = next_min[-1]

    if(next_min + timedelta(minutes=45*start) > df_ultimate.tail(1).index):
        start = len(df_ultimate.tail(len(df_ultimate) - df_ultimate.index.get_loc(next_min)))

    left = df_ultimate.index.get_loc(next_min + timedelta(minutes=45))
    right = df_ultimate.index.get_loc(next_min + timedelta(minutes=45*start))
    
    while(df_ultimate.iloc[left:right]['Low price'].min() < df_ultimate.loc[next_min]['Low price']):
        next_min = df_ultimate.iloc[left:right]['Low price'].min()
    list_days.append(next_min)
    list_min.append(df_ultimate.loc[next_min]['Low price'])
    '''for day in range(min_lenght):
            if(n + day < len(df_ultimate) and flag):
                if(list_prices[n + day] > list_prices[n]):
                    flag = 0
                    list_costraints.append(n + day)
                    list_price_costraints.append(list_prices[n + day])'''
    min_date = next_min
    start = 6
writer.writerow(list_days)
writer.writerow(list_min)
'''writer.writerow(list_costraints)
writer.writerow(list_price_costraints)'''
file.close()