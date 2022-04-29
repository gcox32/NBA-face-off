from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
from datetime import date
import numpy as np
from tqdm import tqdm

# There is some debate as to when the modern era of basketball began. NBA modern era options:
merger = 1977
three_point = 1980
unrestricted_fa = 1989
bulls_breakup = 1999
def_rule_change = 2001

# current year and month
c_year = date.today().year
c_month = date.today().month

# select year data for var 'begin'
# as a default, 'begin' will be set as the year of the addition of the 3-point line (1979-1980 season)

begin = unrestricted_fa

# select your end year
# as a default, 'end' will be set as the current year (2019 at time of creation)

if c_month > 10:
    end = c_year + 1
else:
    end = c_year

years = list(range(begin, end + 1))

################################################## per game stats ########################################################

dfs = []

for year in tqdm(years):
    # URL page we will scraping
    url = "https://www.basketball-reference.com/leagues/NBA_{}_per_game.html".format(year)
    
    # this is the HTML from the given URL
    html = urlopen(url)
    soup = BeautifulSoup(html, features="html.parser")

    # use findALL() to get the column headers
    soup.findAll('tr', limit=2)

    # use getText()to extract the text we need into a list
    headers = [th.getText() for th in soup.findAll('tr', limit=2)[0].findAll('th')]

    # exclude the first column as we will not need the ranking order from Basketball Reference for the analysis
    headers = headers[1:]

    # get the actual data
    # avoid the first header row
    rows = soup.findAll('tr')[1:]
    player_stats = [[td.getText() for td in rows[i].findAll('td')]
            for i in range(len(rows))]
    
    # append a list of player stats
    year_stats = pd.DataFrame(player_stats, columns = headers)
    
    year_stats = year_stats.dropna(how='all')
    
    # add year columns
    year_stats['Year'] = year - 1
    
    # append a list of dfs to be concatenated
    dfs.append(year_stats)

# concat all dfs to create stats df

stats = pd.concat(dfs)

# str split "player" into "last name" and "first name" for organization

last_first = stats.Player.str.split(" ", n = 1, expand = True)
stats['First Name'] = last_first[0]
stats['Last Name'] = last_first[1]
stats.drop(columns = ['Player'], inplace = True)

# reorganize columns so that last name and first name come first before stats

stats = stats[['Last Name','First Name', 'Year', 'Pos', 'Age', 'Tm', 'G', 'GS', 'MP', 
               'FG', 'FGA', 'FG%', '3P', '3PA', '3P%', '2P', '2PA', '2P%', 
               'eFG%', 'FT', 'FTA', 'FT%', 'ORB', 'DRB', 'TRB', 'AST', 'STL', 
               'BLK', 'TOV', 'PF', 'PTS']]

stats = stats.sort_values(['Year', 'Last Name'], ascending = [False, True])
stats = stats.rename(columns = {'MP': 'MPG'})
stats.replace(r'^\s*$', np.nan, regex = True, inplace = True)
float_cols = [2,4] + list(range(6,31))

for col in float_cols:
    stats.iloc[:,col] = stats.iloc[:,col].astype('float')
stats['Full Name'] = stats['First Name'] + " " + stats['Last Name']
pergame = stats[['Last Name', 'First Name', 'Full Name','Year', 'Pos', 'Age', 'Tm', 'G', 'GS', 'MPG',
       'FG', 'FGA', 'FG%', '3P', '3PA', '3P%', '2P', '2PA', '2P%', 'eFG%',
       'FT', 'FTA', 'FT%', 'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV',
       'PF', 'PTS']]
file_loc = '../data/interim/pergame.csv'

pergame.to_csv(file_loc, index=False)

#################################### per 100 possessions stats #########################################################

dfs = []

for year in tqdm(years):
    url = "https://www.basketball-reference.com/leagues/NBA_{}_per_poss.html".format(year)
    
    html = urlopen(url)
    soup = BeautifulSoup(html, features="html.parser")

    soup.findAll('tr', limit=2)

    headers = [th.getText() for th in soup.findAll('tr', limit=2)[0].findAll('th')]
    headers = headers[1:]

    rows = soup.findAll('tr')[1:]
    player_stats = [[td.getText() for td in rows[i].findAll('td')]
            for i in range(len(rows))]
    
    year_stats = pd.DataFrame(player_stats, columns = headers)
    
    year_stats = year_stats.dropna(how='all')
    
    year_stats['Year'] = year - 1

    dfs.append(year_stats)


stats = pd.concat(dfs)

last_first = stats.Player.str.split(" ", n = 1, expand = True)
stats['First Name'] = last_first[0]
stats['Last Name'] = last_first[1]
stats = stats.rename(columns = {'Player':'Full Name'})

stats = stats[['Last Name','First Name', 'Full Name', 'Year', 'Pos', 'Age', 'Tm', 
               'G', 'GS', 'MP', 'FG', 'FGA', 'FG%', '3P','3PA', '3P%', '2P', '2PA',
               '2P%', 'FT', 'FTA', 'FT%', 'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 
               'TOV', 'PF', 'PTS', '', 'ORtg', 'DRtg']]

stats = stats.sort_values(['Year', 'Last Name'], ascending = [False, True])

############################################### advanced stats ######################################################

adv_dfs = []

for year in tqdm(years):
    url = "https://www.basketball-reference.com/leagues/NBA_{}_advanced.html".format(year)
    
    html = urlopen(url)
    soup = BeautifulSoup(html, features="html.parser")

    soup.findAll('tr', limit=2)

    headers = [th.getText() for th in soup.findAll('tr', limit=2)[0].findAll('th')]

    headers = headers[1:]
    rows = soup.findAll('tr')[1:]
    player_stats = [[td.getText() for td in rows[i].findAll('td')]
            for i in range(len(rows))]
    
    year_stats = pd.DataFrame(player_stats, columns = headers)
    
    year_stats = year_stats.dropna(how='all')
    
    year_stats['Year'] = year - 1
    
    adv_dfs.append(year_stats)

adv_stats = pd.concat(adv_dfs)

last_first = adv_stats.Player.str.split(" ", n = 1, expand = True)
adv_stats['First Name'] = last_first[0]
adv_stats['Last Name'] = last_first[1]
adv_stats = adv_stats.rename(columns = {'Player':'Full Name'})

adv_stats = adv_stats[['Last Name', 'First Name', 'Full Name','Year', 'Pos', 'Age', 'Tm', 'G', 'MP',
                       'PER', 'TS%', '3PAr', 'FTr', 'ORB%', 'DRB%', 'TRB%', 'AST%', 'STL%', 
                       'BLK%', 'TOV%', 'USG%', 'OWS', 'DWS', 'WS', 'WS/48', 'OBPM', 
                       'DBPM', 'BPM', 'VORP']]

adv_stats = adv_stats.sort_values(['Year', 'Last Name'], ascending = [False, True])

####################################### merge per100 data ###################################################################

per_100 = pd.merge(stats, adv_stats, on = ['Last Name', 'First Name', 'Full Name','Year','Pos','Tm','Age','G','MP'])

per_100.replace(r'^\s*$', np.nan, regex = True, inplace = True)

float_cols = [3,5] + list(range(7,54))

for col in float_cols:
    per_100.iloc[:,col] = per_100.iloc[:,col].astype('float')

file_loc = "../data/interim/per_100.csv"

per_100.to_csv(file_loc)
