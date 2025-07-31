import pandas as pd
import colorama
import datetime as dt
import time as t
import numpy as np
from functools import reduce
import seaborn as sns
from typing import List
import questionary


# modifica per una migliore visualizzazione dei dati e creazione di una progress bar
pd.set_option("display.precision", 8)


def progress_bar(progress, total, color=colorama.Fore.YELLOW):
    percent = 100 * (progress / float(total))
    bar = '*' * int(percent) + '-' * (100 - int(percent))
    print(color + f"\r|{bar}| {percent:.2f}%", end="\r")
    if progress == total:
        print(colorama.Fore.GREEN + f"\r|{bar}| {percent:.2f}%", end="\r")
        print(colorama.Fore.RESET)

def get_user_inputs() -> dict:
    inputs = {}
    
    type_storico = questionary.select(
        "Quale storico vuoi usare?",
        choices=["Binance", "Coingecko"]
    ).ask()
    inputs["type_storico"] = 0 if type_storico == "Binance" else 1
    
    direction = questionary.select(
        "In che direzione voui calcolare i cumulativi?",
        choices=["Da oggi andando indietro", "Da un giorno specifico in avanti"]
    ).ask()
    inputs["direction"] = 0 if direction == "Da oggi andando indietro" else 1
    
    if inputs["direction"]:
        days = questionary.text("Da che giorni vuoi partire (separati da uno spazio)").ask()
        inputs["days"] = [int(day) for day in days.split()]
    else:
        days = questionary.text("Fino a quali giorni vuoi arrivare? (separati da uno spazio)").ask()
        inputs["days"] = [int(day) for day in days.split()]
        
    all_cumulatives = questionary.confirm("Seleziona che tipo di cumulativi ti servono: Tutti?").ask()
    inputs["all_cumulatives"] = all_cumulatives
    
    if not all_cumulatives:
        cumulatives = questionary.text("Inserisci il numero di giorni dei cumulativi che ti servono (separati da uno spazio)").ask()
        inputs["cumulatives"] = [int(cumulative) for cumulative in cumulatives.split()]
    
    order = questionary.select(
        'Li vuoi ordinati per Score o per performance?',
        choices=["Performance", "Score"]
    ).ask()
    inputs["order"] = 0 if order == "Performance" else 1
    
    return inputs

inputs = get_user_inputs()


# serie di parametri richiesti all'utente per poter generare l'elaborazione desiderata
type_storico = inputs["type_storico"]

direction = inputs["direction"]

days = inputs["days"]

all = inputs["all_cumulatives"]

order = inputs["order"]

# viene caricato lo storico a seconda di quale fonte si desidera usare
if (not type_storico):
    df_principale = pd.read_excel('closes.xlsx', index_col=0)
    df_principale.set_index('Close time', inplace=True)
else:
    df_principale = pd.read_excel('storico.xlsx', index_col=0)

# ciclo per ogni giorno che si desidera analizzare
for day in days:
    start = day
    if (all):
        cumulatives = list(range(start + 1))
        cumulatives.remove(0)
    else:
        cumulatives = inputs["cumulatives"]
        cumulatives = cumulatives.split()
    totale = (len(cumulatives) * 5) - 3
    progresso = 0
    df_for_index = df_principale.tail(start)

    # vengono caricati i dati dai file riguardanti le medie
    df_SMA_fast = pd.read_excel('above_fast.xlsx', index_col=0)
    df_SMA_fast.set_index('Close time', inplace=True)
    df_SMA_medium = pd.read_excel('above_medium.xlsx', index_col=0)
    df_SMA_medium.set_index('Close time', inplace=True)
    df_SMA_slow = pd.read_excel('above_slow.xlsx', index_col=0)
    df_SMA_slow.set_index('Close time', inplace=True)
    df_SMA_fast = df_SMA_fast.T
    df_SMA_medium = df_SMA_medium.T
    df_SMA_slow = df_SMA_slow.T
    df_SMA_fast = df_SMA_fast.iloc[:, len(df_SMA_fast.columns) - start: len(df_SMA_fast.columns)].copy()
    df_SMA_medium = df_SMA_medium.iloc[:, len(df_SMA_medium.columns) - start: len(df_SMA_medium.columns)].copy()
    df_SMA_slow = df_SMA_slow.iloc[:, len(df_SMA_slow.columns) - start: len(df_SMA_slow.columns)].copy()

    # dal file con lo storico vengono calcolate le performance giornaliere e creati i cumulativi
    leaderboard = []
    if not direction:
        for num in cumulatives:
            pd.set_option('display.float_format', lambda x: '%.7f' % x)
            df_24h_sum = df_principale.T
            df_24h_sum = ((df_24h_sum.iloc[:, len(df_24h_sum.columns) - 1] - df_24h_sum.iloc[:,
                                                                            len(df_24h_sum.columns) - num]) / df_24h_sum.iloc[
                                                                                                            :,
                                                                                                            len(df_24h_sum.columns) - num]) * 100
            df_24h_sum = df_24h_sum.sort_values(ascending=False)
            df_24h_sum = df_24h_sum.to_frame()
            df = df_24h_sum.copy()[[]]
            df_24h_sum.columns = ['Cumulative']
            df_24h_sum.reset_index(drop=True, inplace=True)
            ranking = pd.DataFrame(range(1, 1 + len(df_24h_sum)))
            ranking.columns = ['Rank']
            ranking['Cumulative'] = df_24h_sum['Cumulative']
            df_24h_sum = pd.concat([df_24h_sum, ranking], axis=1)
            df_24h_sum.columns = ['Cumulative', 'Rank', 'Trash']  # cambiare cumulative con la data
            df_24h_sum.drop('Trash', axis=1, inplace=True)
            df_24h_sum.index = df.index
            leaderboard.append(df_24h_sum)
            progresso += 1
            progress_bar(progresso, totale)
    else:
        for num in cumulatives:
            pd.set_option('display.float_format', lambda x: '%.10f' % x)
            df_24h_sum = df_principale.T
            df_24h_sum = ((df_24h_sum.iloc[:, (len(df_24h_sum.columns) - 1 - start + num)] - df_24h_sum.iloc[:, (
                                                                                                                        len(df_24h_sum.columns) - 1 - start)]) / df_24h_sum.iloc[
                                                                                                                                                                :,
                                                                                                                                                                (
                                                                                                                                                                        len(df_24h_sum.columns) - 1 - start)]) * 100
            df_24h_sum = df_24h_sum.sort_values(ascending=False)
            df_24h_sum = df_24h_sum.to_frame()
            df = df_24h_sum.copy()[[]]
            df_24h_sum.columns = ['Cumulative']
            df_24h_sum.reset_index(drop=True, inplace=True)
            ranking = pd.DataFrame(range(1, 1 + len(df_24h_sum)))
            ranking.columns = ['Rank']
            ranking['Cumulative'] = df_24h_sum['Cumulative']
            df_24h_sum = pd.concat([df_24h_sum, ranking], axis=1)
            df_24h_sum.columns = ['Cumulative', 'Rank', 'Trash']
            df_24h_sum.drop('Trash', axis=1, inplace=True)
            df_24h_sum.index = df.index
            leaderboard.append(df_24h_sum)
            progresso += 1
            progress_bar(progresso, totale)

    # i cumulativi vengono salvati in un file
    cycles = leaderboard
    with pd.ExcelWriter('leaderboards.xlsx') as writer:
        counter = 0
        for df in leaderboard:
            df.to_excel(writer, sheet_name=str(cumulatives[counter]) + 'd')
            counter += 1
            progresso += 1
            progress_bar(progresso, totale)

    # ai cumulativi viene inizialmente aggiunta una colonna con il rank di ogni coin
    df_totale = pd.read_excel('leaderboards.xlsx', sheet_name=str(cumulatives[0]) + 'd')
    titolo = str(cumulatives[0]) + 'd'
    df_totale.columns = ['Coin', titolo, 'Rank']
    df_totale.drop('Rank', inplace=True, axis=1)
    df_totale.set_index('Coin', inplace=True)
    for num in range(len(cumulatives)):
        if (cumulatives[num] != cumulatives[0]):
            second_df = pd.read_excel('leaderboards.xlsx', sheet_name=str(cumulatives[num]) + 'd')
            titolo = str(cumulatives[num]) + 'd'
            second_df.columns = ['Coin', titolo, 'Rank']
            second_df.drop('Rank', inplace=True, axis=1)
            second_df.set_index('Coin', inplace=True)
            df_totale = df_totale.merge(second_df, on='Coin')
            df_totale = df_totale.copy()
            progresso += 1
            progress_bar(progresso, totale)

    # creazione primo dati primo giorno su cui poi attaccare gli altri
    first = pd.read_excel('leaderboards.xlsx', sheet_name=str(cumulatives[0]) + 'd')
    first.columns = ['Coin', 'Cumulative', 'Rank']
    first.drop('Rank', inplace=True, axis=1)
    first.set_index('Coin', inplace=True)
    first_temp = first['Cumulative']
    first_temp = first_temp.to_frame()
    first_temp.columns = ['24h_change']
    first_temp = first_temp.reset_index()
    first_temp = first_temp.sort_values(by='24h_change', ascending=False)
    conditions = [
        (first_temp.index < 10),
        (first_temp.index >= 10) & (first_temp.index < 15),
        (first_temp.index >= 15) & (first_temp.index < 20)
    ]
    values = [3, 2, 1]
    first_temp['Day_rank'] = np.select(conditions, values)
    first_temp.drop('24h_change', inplace=True, axis=1)
    first_day_SMA_fast_index = df_SMA_fast.columns[0]
    df_first_day_SMA_fast = df_SMA_fast[first_day_SMA_fast_index]
    df_first_day_SMA_fast = df_first_day_SMA_fast.to_frame()
    df_first_day_SMA_fast.index.name = 'Coin'
    df_first_day_SMA_fast.columns = ['Above SMA_fast']
    first_day_SMA_medium_index = df_SMA_medium.columns[0]
    df_first_day_SMA_medium = df_SMA_medium[first_day_SMA_medium_index]
    df_first_day_SMA_medium = df_first_day_SMA_medium.to_frame()
    df_first_day_SMA_medium.index.name = 'Coin'
    df_first_day_SMA_medium.columns = ['Above SMA_medium']
    first_day_SMA_slow_index = df_SMA_slow.columns[0]
    df_first_day_SMA_slow = df_SMA_slow[first_day_SMA_slow_index]
    df_first_day_SMA_slow = df_first_day_SMA_slow.to_frame()
    df_first_day_SMA_slow.index.name = 'Coin'
    df_first_day_SMA_slow.columns = ['Above SMA_slow']
    first = first.merge(df_first_day_SMA_fast, on='Coin')
    first = first.merge(df_first_day_SMA_medium, on='Coin')
    first = first.merge(df_first_day_SMA_slow, on='Coin')

    # ogni cumulativo viene aggiunto a quello del primo giorno
    leaderboard = []
    df_score_cum = first_temp.copy()
    df_score_cum.set_index('Coin', inplace=True)
    df_score_cum.columns = ['Score']
    df_score_cum['Score'] = df_score_cum['Score'].astype(float)
    df_score_temp = df_score_cum['Score'].copy()
    df_score_temp = df_score_temp.to_frame()
    for num in range(len(cumulatives) - 1):
        df_score_temp['Score'] = 0
        first_df = pd.read_excel('leaderboards.xlsx', sheet_name=str(cumulatives[num]) + 'd')
        second_df = pd.read_excel('leaderboards.xlsx', sheet_name=str(cumulatives[num + 1]) + 'd')
        first_df.columns = ['Coin', 'Cumulative', 'Rank1']
        second_df.columns = ['Coin', 'Cumulative', 'Rank2']
        first_temp = first_df.copy()
        second_temp = second_df.copy()
        first_temp.drop('Rank1', inplace=True, axis=1)
        second_temp.drop('Rank2', inplace=True, axis=1)
        first_temp.set_index('Coin', inplace=True)
        second_temp.set_index('Coin', inplace=True)
        first_temp.columns = ['Cumulative1']
        second_temp.columns = ['Cumulative2']
        first_temp = first_temp.merge(second_temp, on='Coin')
        first_temp['24h_change'] = (first_temp['Cumulative2'] - first_temp['Cumulative1'])
        first_temp.drop(['Cumulative1', 'Cumulative2'], inplace=True, axis=1)
        first_temp = first_temp.sort_values(by='24h_change', ascending=False)
        first_temp = first_temp.reset_index()
        conditions = [
            (first_temp.index < 10),
            (first_temp.index >= 10) & (first_temp.index < 15),
            (first_temp.index >= 15) & (first_temp.index < 20)
        ]
        values = [3, 2, 1]
        first_temp['Day_rank'] = np.select(conditions, values)
        first_temp.drop('24h_change', inplace=True, axis=1)
        first_temp.set_index('Coin', inplace=True)
        first_df.drop('Cumulative', inplace=True, axis=1)
        df = second_df.merge(first_df, on='Coin')
        df['Change'] = (df['Rank1'] - df['Rank2']) / 10
        conditions = [
            (df['Change'].astype(float) > 0),
            (df['Change'].astype(float) < 0),
            (df['Change'].astype(float) == 0)
        ]
        values = [1, -1, 0]
        df['Type of change'] = np.select(conditions, values)
        conditions = [
            (df.index < 10),
            (df.index >= 10) & (df.index < 15),
            (df.index >= 15) & (df.index < 20)
        ]
        values = [3, 2, 1]
        df['Top 10'] = np.select(conditions, values)
        df.drop(['Rank1', 'Rank2'], inplace=True, axis=1)
        df.set_index('Coin', inplace=True)
        df_score_temp_change = df['Change'].copy()
        df_score_temp_change.index = df.index
        df_score_temp_type = df['Type of change'].copy()
        df_score_temp_type.index = df.index
        df_score_temp = df_score_temp_change  # .add(df_score_temp_type)
        first_day_SMA_fast_index = df_SMA_fast.columns[num + 1]
        df_first_day_SMA_fast = df_SMA_fast[first_day_SMA_fast_index]
        df_first_day_SMA_fast = df_first_day_SMA_fast.to_frame()
        df_first_day_SMA_fast.index.name = 'Coin'
        df_first_day_SMA_fast.columns = ['Above SMA_fast']
        first_day_SMA_medium_index = df_SMA_medium.columns[num + 1]
        df_first_day_SMA_medium = df_SMA_medium[first_day_SMA_medium_index]
        df_first_day_SMA_medium = df_first_day_SMA_medium.to_frame()
        df_first_day_SMA_medium.index.name = 'Coin'
        df_first_day_SMA_medium.columns = ['Above SMA_medium']
        first_day_SMA_slow_index = df_SMA_slow.columns[num + 1]
        df_first_day_SMA_slow = df_SMA_fast[first_day_SMA_slow_index]
        df_first_day_SMA_slow = df_first_day_SMA_slow.to_frame()
        df_first_day_SMA_slow.index.name = 'Coin'
        df_first_day_SMA_slow.columns = ['Above SMA_slow']
        df_day_rank = first_temp['Day_rank'].copy()
        df = df.merge(df_first_day_SMA_fast, on='Coin')
        df = df.merge(df_first_day_SMA_medium, on='Coin')
        df = df.merge(df_first_day_SMA_slow, on='Coin')
        df = df.merge(first_temp, on='Coin')
        df_score_temp_SMA_fast = df['Above SMA_fast']
        df_score_temp_SMA_medium = df['Above SMA_medium']
        df_score_temp_SMA_slow = df['Above SMA_slow']
        df_score_temp_top10 = df['Top 10']
        df_score_temp_day_rank = df['Day_rank']
        df_score_temp = reduce(lambda a, b: a.add(b, fill_value=0),
                            [df_score_temp, df_score_temp_SMA_fast, df_score_temp_SMA_medium, df_score_temp_SMA_slow,
                                df_score_temp_top10, df_score_temp_day_rank])
        df_score_temp = df_score_temp.to_frame()
        df_score_temp.columns = ['Score']
        df_score_cum = df_score_cum.add(df_score_temp)
        df = df.merge(df_score_cum, on='Coin')
        if (order):
            df = df.sort_values(by='Score', ascending=False)
        leaderboard.append(df)
        progresso += 1
        progress_bar(progresso, totale)

    # creo il file di base con i cumulativi suddivisi per giorno e un foglio con la performance delle coin giorno per giorno
    if (start < 10):
        t.sleep(1)
    if (direction):
        filename = 'leaderboard_forward.xlsx'
    else:
        filename = 'leaderboard_backward.xlsx'
    with pd.ExcelWriter(filename) as writer:
        df_totale.to_excel(writer, sheet_name='Aggregate')
        first.to_excel(writer, sheet_name=str(cumulatives[0]) + 'd')
        counter = 1
        for df in leaderboard:
            df.to_excel(writer, sheet_name=str(cumulatives[counter]) + 'd')
            counter += 1
            progresso += 1
            progress_bar(progresso, totale)

    # creo il file finale aggregando tutti i cumulativi, i punteggi e lo score totale
    list_cum = []
    for cum in cumulatives:
        df_sheet = pd.read_excel(filename, sheet_name=str(cum) + 'd')
        df_sheet = df_sheet.rename(columns={'Change': 'Change ' + str(cum) + 'd'})
        df_sheet = df_sheet.rename(columns={'Score': 'Score ' + str(cum) + 'd'})
        if (cum != 1):
            name_col = 'Change ' + str(cum) +'d'
            df_sheet.drop([name_col, 'Type of change', 'Top 10', 'Above SMA_fast', 'Above SMA_medium', 'Above SMA_slow', 'Day_rank'], inplace=True,
                    axis=1)
        else:
            df_sheet.drop(['Above SMA_fast', 'Above SMA_medium', 'Above SMA_slow'], inplace=True, axis=1)
        list_cum.append(df_sheet)
    df_cums = pd.concat(list_cum, axis=1)
    if (direction):
        filename = 'cumulative_changes_forward_' + str(day) + '.xlsx'
    else:
        filename = 'cumulative_changes_backward' + str(day) + '.xlsx'
    df_cums.to_excel(filename)

    def generate_random_palette(n_colors):
        return ["#"+"".join(map(lambda x: format(int(x), '02x'), np.random.randint(0, 256, size=3))) for i in range(n_colors)]

    # coloro le celle in base al nome della coin
    df = pd.read_excel(filename)
    color_palette = generate_random_palette(n_colors=len(df.iloc[:, 1].unique()))
    name_colors = {}
    for i, name in enumerate(df.iloc[:, 1].unique()):
        color_index = i % len(color_palette)
        name_colors[name] = color_palette[color_index]
    def highlight_name(val):
        return 'background-color: {}'.format(name_colors[val])
    coin_columns = [column for column in df.columns if column.startswith('Coin.') or column.startswith('Coin')]
    styled_df = df.style.applymap(highlight_name, subset=coin_columns)
    styled_df.to_excel(filename, index=False)
