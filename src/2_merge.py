import numpy as np
import pandas as pd

interim = '../data/interim/'
pergame_file = interim + 'pergame.csv'
per100_file = interim + 'per_100.csv'

pergame = pd.read_csv(pergame_file)
per100 = pd.read_csv(per100_file).drop(['Unnamed: 0', 'Unnamed: 32'], axis = 1).dropna(subset=['Last Name', 'PER'])

per100_columns = ['MP', 'FG', 'FGA', 'FG%', '3P', '3PA', '3P%', '2P', '2PA', '2P%',
       'FT', 'FTA', 'FT%', 'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV',
       'PF', 'PTS']
adj_per100_cols = []

for col in per100.columns:
    if col in per100_columns:
        col = col + '_per100'
    adj_per100_cols.append(col)

per100.columns = adj_per100_cols

df = pd.merge(pergame, per100, on=['Last Name', 'First Name', 'Full Name','Year','Pos','Tm','Age','G', 'GS'])

nanlist = df.isnull().sum()
nanlist = nanlist.where(nanlist > 0).dropna()
print('Number of features containing NaN values:',(len(nanlist)),'\n')
print(nanlist)