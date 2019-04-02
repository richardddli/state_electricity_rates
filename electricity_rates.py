#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan  4 02:02:07 2019

@author: richard
"""

### 
### for f in *; do xlsx2csv "$f/Table_5_06_A.xlsx" "$f/Table_5_06_A.csv"; done 
# july2012 is first month with new namign convention
###
import pandas as pd
from dateutil import parser
import os
import glob
import xlrd, csv
import datetime
from statsmodels.tsa.seasonal import seasonal_decompose
import matplotlib.pyplot as plt
from scipy.stats import linregress

months = ['null', 'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']

### new data
path = 'C:/Users/richa/Documents/State costs/data/new data/*'
dirs = [os.path.join(dir, 'Table_5_06_A.csv') for dir in glob.glob(path)]

# initialize df
df_or = pd.read_csv(dirs[0])
df = df_or.iloc[3:65, [0,9]]
df.columns = ['State', df_or.iloc[2, 1]]

# build database from new data
for dir in dirs[1:]:
    data = pd.read_csv(dir)
    if (df.iloc[:, 0] == data.iloc[3:65, 0]).all():
        # all sectors
        df[data.iloc[2, 1]] = data.iloc[3:65, 9]  ## change column '9' if using resi, comm, or ind rates
    else:
        print(data.iloc[2,1])

df.columns = ['State'] + [parser.parse(month, default=datetime.datetime(2016, 1, 1, 0, 0)).date() for month in df.columns[1:]]
df.reset_index(drop=True, inplace=True)

# old data: convert xls to csv
def csv_from_excel(excel_file):
    workbook = xlrd.open_workbook(excel_file)
    worksheet = workbook.sheet_by_index(0)
    with open(excel_file[:-4] + '.csv', 'w') as your_csv_file:
        wr = csv.writer(your_csv_file, quoting=csv.QUOTE_ALL)
        for rownum in range(worksheet.nrows):
            wr.writerow([str(entry) for entry in worksheet.row_values(rownum)])

path = 'C:/Users/richa/Documents/State costs/data/old data/*'
dirs = []
possible_filenames = ['epmxlfile5_6_a.xls', 'EPMXLFile 5_6_A.xls', 'EPMXLFile 5_6_A_OLD.xls']
for dir in glob.glob(path):
    for fi in possible_filenames:
        if os.path.exists(os.path.join(dir, fi)):
            dirs.append(os.path.join(dir, fi))
#[csv_from_excel(dir) for dir in dirs]


### add old data to database
for dir in dirs:
    dir = dir[:-4] + '.csv'
    data = pd.read_csv(dir, encoding="latin-1")
    if 'Table' in data.iloc[0,0]:
        data = data[1:].reset_index(drop=True)
    if (df.iloc[:, 0] == data.iloc[5:67, 0].reset_index(drop=True)).all():
        # all sectors
        date = datetime.date.fromordinal(693594 + int(float(data.iloc[4, 1])))
        df[date] = data.iloc[5:67, 9].reset_index(drop=True)  ## change column '9' if using resi, comm, or ind rates
    else:
        print(dir)
    
    
#cleanup database
df.set_index('State', inplace=True)
df = df.astype('float')
df.columns = pd.to_datetime(df.columns)
df=df.reindex(columns=sorted(df.columns))




# TRENDS
states = df.index
trends = pd.DataFrame()
for state in states:
    s = seasonal_decompose(df.loc[state], model='additive')
    trends[state] = s.trend
trends = trends.iloc[6:-6]


# LIN REGRESSION
regions = ['New England', 'Middle Atlantic', 'West North Central', 'East North Central', 'South Atlantic', 'East South Central', 'West South Central', 'Mountain', 'Pacific Contiguous', 'Pacific Noncontiguous', 'U.S. Total']
trends = trends.drop(regions, axis=1)
states = trends.columns

trends2 = trends.reset_index()
trends2 = trends2.loc[57:]

reg = pd.DataFrame(columns=['slope', 'intercept', 'rvalue', 'pvalue', 'stderr'])
for state in states: 
    reg.loc[state] = linregress(trends2.index, trends2[state])

reg.sort_values('slope', ascending=False, inplace=True)


### PLOTTING CONVENIENCE FUNCTIONS
def plot2(i1, i2, i3=None, i4=None, title=""):
    fig, ax = plt.subplots()
    df = trends.iloc[:, i1:i2]
    if i3 is not None:
        df2 = trends.iloc[:, i3:i4]
        df = pd.concat([df, df2], axis=1)
    df = df.sort_values('2018-03-01', ascending=False, axis=1)
    df.plot(ax=ax)
    ax.legend(bbox_to_anchor=(1.44, 1.03))
    ax.set_ylabel('cents/kWh')
    if title is not "":
        ax.set_title(title)
    return fig, ax

def plot3(states, title=""):
    fig, ax = plt.subplots()
    df = trends[states]
    df = df.sort_values('2018-03-01', ascending=False, axis=1)
    df.plot(ax=ax)
    ax.legend(bbox_to_anchor=(1.44, 1.03))
    ax.set_ylabel('cents/kWh')
    if title is not "":
        ax.set_title(title)
    return fig, ax

states = {
        'AK': 'Alaska',
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AS': 'American Samoa',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DC': 'District of Columbia',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'GU': 'Guam',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MP': 'Northern Mariana Islands',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NA': 'National',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'PR': 'Puerto Rico',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VI': 'Virgin Islands',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming'
}

##### PROBLEM EIA FILES MANUALLY EDITED:

#Apr 09: removed footnotes (LA TX Total)
#Jan 04 and Feb 04: removed footnotes (MD CA)
#Oct 04: changed date (38169, 37803)


