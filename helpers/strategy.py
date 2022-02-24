# strategy.py: takes in parameters for a trading day (i.e. account, current date signals)
#                     and executes trade decision
#             # trading_day() --> 

# Read relevant csv files into dictionaries

import csv
import datetime
import timedelta
import indicators

# Pull in symbols.csv for iteration
def getSymbols():

    lstSymbols = []
    reader = csv.DictReader(open('data/symbols.csv', mode='r', encoding='utf-8-sig'))
    lstSymbols = list(reader)

    return lstSymbols

# Read in the Daily-level file in full, build list of dictionaries
def getDaily():

    lstDaily = []
    reader = csv.DictReader(open('data/daily.csv', mode='r', encoding='utf-8-sig'))
    lstDaily = list(reader)

    return lstDaily

# Build sublist of dictionaries based on a dataset, symbol/ticker, latest date, and # of days
def setTradingData(data, symbol, latestdate, timewindow):

    lstReturn = []

    for entry in data:

        if entry["symbol"] == symbol and \
            datetime.datetime.fromtimestamp(int(entry["time"])) <= latestdate \
                and datetime.datetime.fromtimestamp(int(entry["time"])) > \
                (latestdate - datetime.timedelta(days=timewindow)):
            lstReturn.append(entry)
    
    return lstReturn

# Rudimentary test function to take a symbol and point in time date to acquire indicators
def strategyMK1(symbol, latestdate):

    lstDaily = getDaily()

    lst1 = setTradingData(lstDaily, symbol, latestdate, 1)
    lst2 = setTradingData(lstDaily, symbol, latestdate, 2)
    lst5 = setTradingData(lstDaily, symbol, latestdate, 5)
    lst10 = setTradingData(lstDaily, symbol, latestdate, 10)
    lst20 = setTradingData(lstDaily, symbol, latestdate, 20)
    lst50 = setTradingData(lstDaily, symbol, latestdate, 50)
    lst100 = setTradingData(lstDaily, symbol, latestdate, 100)
    lst200 = setTradingData(lstDaily, symbol, latestdate, 200)

    # Print latest price data
    print(lst1)

    # Get rising, falling past 5 days
    print("5-Day Rising:", indicators.risingCheck(lst5))
    print("5-Day Falling:", indicators.fallingCheck(lst5))

    # Get 10-day ATR
    print("10-Day ATR:", round(indicators.getATR(lst10), 2))

    # Get 50, 200 day SMAs and EMAs
    print("20-Day SMA:", round(indicators.getSMA(lst20), 2))
    print("50-Day SMA:", round(indicators.getSMA(lst50), 2))
    print("100-Day SMA:", round(indicators.getSMA(lst100), 2))
    print("20-Day Rolling 100-Day EMA:", round(indicators.getEMA(lst100, 20), 2))
    print("50-Day Rolling 100-Day EMA:", round(indicators.getEMA(lst100, 50), 2))
    print("20-Day Rolling 200-Day EMA:", round(indicators.getEMA(lst200, 20), 2))
    print("50-Day Rolling 200-Day EMA:", round(indicators.getEMA(lst200, 50), 2))

    # Get 200 day RSI
    print("20-Day Rolling 200-Day RSI:", round(indicators.getRSI(lst200, 20), 2))
    print("50-Day Rolling 200-Day RSI:", round(indicators.getRSI(lst200, 50), 2))

    # Check most recent candlestick patterns (today, yesterday)
    print("38.2% Candle:", indicators.get382(lst1))
    print("Engulfing Candle:", indicators.getEngulfing(lst2[0], lst2[1]))
    print("Above/Below Candle:", indicators.getAboveBelow(lst2[0], lst2[1]))


def checkGoldenCross(symbol, latestdate):

    # Pull latest daily list, pull down the full dataset for the symbol
    lstDaily = getDaily()
    lstSymbol = setTradingData(lstDaily, symbol, latestdate, 99999)
    
    # Starting with the oldest data, iteratively check the 20-Day EMA and store in list
    lst20EMA = []
    lstWindow = lstSymbol[0:20]
    intCounter = 20

    while intCounter < len(lstSymbol):
        lst20EMA.append(indicators.getEMA(lstWindow, 20))
        lstWindow.pop(0)
        lstWindow.append(lstSymbol[intCounter])
        intCounter += 1

    # Starting with the oldest data, iteratively check the 100-Day EMA and store in list
    lst100EMA = []
    lstWindow = lstSymbol[0:100]
    intCounter = 100

    while intCounter < len(lstSymbol):
        lst100EMA.append(indicators.getEMA(lstWindow, 100))
        lstWindow.pop(0)
        lstWindow.append(lstSymbol[intCounter])
        intCounter += 1

    # Iterate through historical EMA lists to identify crossing points

    intCounter = 0
    boolGolden = False
    boolDeath = False

    return lst20EMA, len(lst20EMA)

lstSymbols = getSymbols()
dateLatest = datetime.datetime(2022, 2, 21, 23, 59, 59)
# print(datetime.datetime.fromtimestamp(1645488000))

print(checkGoldenCross("BTC-USD", dateLatest))