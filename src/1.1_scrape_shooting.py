"""This isn't working yet."""

from bs4 import BeautifulSoup, Comment
import pandas as pd
import numpy as np
import requests
import multiprocessing as mp
from multiprocessing import Pool, freeze_support

pd.set_option('mode.chained_assignment', None)

def scrape_shooting_table(url_name):
    url, name = url_name[0], url_name[1]
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    print(soup)
    placeholder = soup.select_one('#all_shooting .placeholder')
    if placeholder is not None: # some of the urls do not contain shooting stats tables
        
        comment = next(elem for elem in placeholder.next_siblings if isinstance(elem, Comment))
        table_soup = BeautifulSoup(comment, 'html.parser')

        headers = [th.getText() for th in table_soup.findAll('th')]
        stop1 = headers.index('Career')  # there is a variable number of seasons to consider; 'Career'
                                        # is the last 'th' after each season before format changes
        seasons = headers[40:stop1] # seasons, which belong in rows but are also classified as 'th'
        headers = headers[12:40] # headers we actually want
        
        data = [] # data for each header

        rows = table_soup.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if cells:
                data.append([cell.text for cell in cells])

        stop2 = [a for (a, b) in enumerate(data) if b[0]==''][0]
        data = data[:stop2] # leave out career averages/totals

        shooting_df = pd.DataFrame(data, columns = headers)
        shooting_df['Year'] = seasons
        shooting_df.Year = pd.to_numeric(shooting_df.Year.str[:4]) # converting '2009-2010' string to '2009' integer
        shooting_df['Full Name'] = name

        df = shooting_df.iloc[:,[1,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29]]

        df.columns = ['Tm','FG%','Dist.','2P_A','0-3_A',
                      '3-10_A','10-16_A','16-3pt_A','3P_A','2P%','0-3%','3-10%','10-16%','16-3pt%',
                      '3P%',"Astd_2P",'Dunk%','Dunks_Md',"Astd_3P",'%Corner3_A','Corner_3P%','Heaves_A', 
                      'Heaves_Md','Year','Full Name']

        df = df[['Full Name','Year','Tm','FG%','Dist.','2P_A','0-3_A','3-10_A', '10-16_A', '16-3pt_A', 
                 '3P_A', '2P%', '0-3%', '3-10%', '10-16%', '16-3pt%','3P%', "Astd_2P", 'Dunk%', 
                 'Dunks_Md', "Astd_3P", '%Corner3_A', 'Corner_3P%', 'Heaves_A', 'Heaves_Md']]

        return df

if __name__ == "__main__":
    freeze_support()
    
    fileloc = '../data/interim/pergame.csv'
    df = pd.read_csv(fileloc).dropna(subset=['Last Name',])


    shooting_urls = []
    for last, first in zip(df['Last Name'].values, df['First Name'].values):
        id = last.lower()[:5] + first.lower()[:2] + '01'
        url = 'https://www.basketball-reference.com/players/' + id[0] + '/' + id + '.html'
        shooting_urls.append(url)

    df['shooting_url'] = shooting_urls
    df['Full Name'] = df['First Name'] + ' ' + df['Last Name']

    dfs = []
    iterable = [(i, j) for i, j in zip(df['shooting_url'].values, df['Full Name'].values)]

    df = scrape_shooting_table(iterable[0])
    print(df.head())
    raise SystemExit
    num_processes = mp.cpu_count()
    num_partitions = num_processes

    with Pool(num_processes) as pool:
        dfs = pool.map(scrape_shooting_table, iterable)

    pool.close()

    shot_df = pd.concat(dfs)
    shot_df = shot_df.replace('',np.nan)
    shot_df.iloc[:,range(3,25)] = shot_df.iloc[:,range(3,25)].astype('float')
    shooting = shot_df[shot_df['Dist.'].notnull()]

    file_loc = '../data/interim/shooting.csv'

    shooting.to_csv(file_loc)