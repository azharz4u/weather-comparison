"""Scrape climate data from Wikipedia pages and return as a pandas dataframe"""

import re
import datetime
import requests
import calendar
import pandas as pd
from bs4 import BeautifulSoup


def data_test_harness(cities):
    """Takes a list of cities to return data for.
    
    Returns a dictionary of dataframes, indexed by city name. Each dataframe contains climate data."""
    temp_df = pd.DataFrame(
        data={
            'Bristol': [4, 3, 2, 4],
            'London': [5, 3, 3, 6],
            'Auckland': [8, 4, 7, 9],
            'Wellington': [10, 9, 6, 8]
        },
        index=['Q1', 'Q2', 'Q3', 'Q4'])
    city_data = {}
    for city in cities:
        city_data[city] = pd.DataFrame(data={
            var: temp_df[city]
            for var in ['high', 'low', 'precipitation']
        })
    return city_data


def wiki_scraper(cities):
    dfs = {}
    for city in cities:
        source_code = requests.get('https://en.wikipedia.org/wiki/' + city)
        soup = BeautifulSoup(source_code.text)
        table = soup.find("table", {"class": "wikitable collapsible"})
        rawdat = []
        for row in table.find_all('tr'):
            rawdat.append(row.text.split('\n'))

        #filter the list items
        filtered_data = []
        regex = re.compile(r'\(([0-9.-]+)\)')
        for l in rawdat:
            #drop blanks
            l1 = filter(None, l)

            #drop imperial measures
            l2 = [x for x in l1 if not regex.match(x)]

            #drop non-data rows
            if len(l2) < 12:
                pass
            else:
                filtered_data.append(l2[:-1])
        df = pd.DataFrame(filtered_data).set_index(0).T.convert_objects(
            convert_numeric=True)
        dfs[city] = df.assign(City=city)

    #Shift Southern hemisphere cities to match Northern hemisphere
    d = [calendar.month_abbr[i] for i in range(1, 13)]
    month_map = dict(zip(d, d[6:] + d[:6]))
    for c in ['Melbourne', 'Wellington']:
        dfs[c].loc[:, 'Month'] = dfs[c].loc[:, 'Month'].map(month_map)

    alldat = pd.concat([v for k, v in dfs.items()], ignore_index=True)
    alldat['Average precipitation mm (inches)'] = alldat[
        'Average precipitation mm (inches)'].combine_first(
            alldat['Average rainfall mm (inches)'])
    alldat.drop('Average rainfall mm (inches)', axis=1, inplace=True)
    alldat.dropna(axis=1, inplace=True)
    alldat['Month'] = alldat['Month'].apply(
        lambda x: datetime.datetime.strptime(x, '%b'))
    alldat['Average precipitation mm (inches)'] = alldat[
        'Average precipitation mm (inches)'].div(25.4)  # convert to inches

    return alldat