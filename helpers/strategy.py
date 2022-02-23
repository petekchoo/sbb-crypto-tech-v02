# strategy.py: takes in parameters for a trading day (i.e. account, current date signals)
#                     and executes trade decision
#             # trading_day() --> 

# Read relevant csv files into dictionaries

import csv
import datetime
import timedelta
import indicators

# Read in the Daily-level file in full, build list of dictionaries
def getDaily():

    lstDaily = []
    reader = csv.DictReader(open('data/daily.csv', mode='r', encoding='utf-8-sig'))
    lstDaily = list(reader)

    return lstDaily

# Build sublist of dictionaries based on a dataset, symbol/ticker, and timeframe
def setTradingData(data, symbol, timewindow):

    lstReturn = []

    for entry in data:

        if entry["symbol"] == symbol and \
            datetime.datetime.fromtimestamp(int(entry["time"])) >= \
                (datetime.datetime.now() - datetime.timedelta(days=timewindow)):
            lstReturn.append(entry)
    
    return lstReturn

def strategyMK1():

    # Check for rising, falling past 5 days

    return False