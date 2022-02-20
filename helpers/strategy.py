# strategy.py: takes in parameters for a trading day (i.e. account, current date signals)
#                     and executes trade decision
#             # trading_day() --> 

# Read relevant csv files into dictionaries

import csv
import datetime
import timedelta
from helpers.indicators import fallingCheck, risingCheck, getATR, getSMA, getEMA

lstDaily = []
reader = csv.DictReader(open('data/daily.csv', mode='r', encoding='utf-8-sig'))
lstDaily = list(reversed(list(reader)))

lstBTC100 = []
account = None

for entry in lstDaily:

    if entry["symbol"] == 'BTC-USD' and \
        datetime.datetime.fromtimestamp(int(entry["time"])) >= \
            (datetime.datetime.now() - datetime.timedelta(days=100)):
        lstBTC100.append(entry)

def returnIndicators(data):

    return risingCheck(data), fallingCheck(data), \
        getATR(data), getSMA(data), getEMA(data, 20)

def runStrategy():
    return returnIndicators(lstBTC100)