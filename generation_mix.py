# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
from scipy.stats import linregress

## convert MW of generation type to percentages: this takes time
def calculate_percentages(data = 'C:/Users/richa/Documents/State costs/data/annual_generation_state.csv'):
    df_or = pd.read_csv(data, usecols = ['Year','State','Producer','Fuel','MWh'])
    df_or['MWh'] = df_or['MWh'].str.replace(',','').replace('.','0').astype(float)
    
    # filter data
    df = df_or[(df_or.Producer == 'Total Electric Power Industry') & (df_or.Year >= 2001)]
    df.drop('Producer', axis=1, inplace=True)
    
    # calculate percentage generation per year
    coal = 'Coal'
    for i, row in df.iterrows():
        if row.State == '  ':
            continue
        total = 'Total'
        df.loc[i, '%'] = row.MWh / df.query('State == @row.State & Year == @row.Year & Fuel == @total').MWh.iloc[0]
    df.to_csv('C:/Users/richa/Documents/State costs/data/percentages.csv')

# import percentages from above function
per = pd.read_csv('C:/Users/richa/Documents/State costs/data/percentages.csv', index_col='i')
per.loc[per.State=='US-TOTAL', 'State'] = 'US-Total'

# restructure to usable df
states = sorted(list(set(per.State)))
years = sorted(list(set(per.Year)))
coal = pd.DataFrame()
for i, row in per[per.Fuel == 'Coal'].iterrows():  ## edit this to look at other generation sources
    if row.Fuel == 'Coal':
        coal.loc[row.State, row.Year] = row['%']


# finding average & slope of coal generation
coal_stats = pd.DataFrame()
year1 = 2001
year2 = 2009
for i, row in coal.iterrows():
    coal_stats.loc[row.name, 'avg1'] = row.loc[year1:].mean()
    coal_stats.loc[row.name, 'avg2'] = row.loc[year2:].mean()
    coal_stats.loc[row.name, 'slope1'] = linregress(range(year1, 2018), row.loc[year1:])[0]
    coal_stats.loc[row.name, 'slope2'] = linregress(range(year2, 2018), row.loc[year2:])[0]


#VARIABLES TO TEST RELATIONSHIP WITH PRICES:
#
#% of coal production (average)
#absolute MWh of coal production (average)
#slope of change in coal production
#all other fuels