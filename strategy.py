import csv, indicators, accounts
from datetime import datetime, timedelta

def getSymbols():
    """
    Pull in symbols.csv for iteration

    Returns:
        list: list of symbols
    """
    lstSymbols = []
    reader = csv.DictReader(open('data/symbols.csv', mode='r', encoding='UTF-8'))
    lstSymbols = list(reader)
    return lstSymbols


def getDaily():
    """
    Read in the Daily-level file in full, build list of dictionaries

    Returns:
        list: list of candles
    """
    lstDaily = []
    reader = csv.DictReader(open('data/daily.csv', mode='r', encoding='UTF-8'))
    lstDaily = list(reader)
    return lstDaily


def setTradingData(data, symbol, latestdate, timeWindow):
    """
    Build sublist of dictionaries based on a dataset, symbol/ticker, latest date, and # of days

    Args:
        data (list): list of candles
        symbol (str): symbol to subset
        latestdate (datetime): most recent period to include
        timeWindow (int): number of periods to include, starting from latestdate, if value is "ALL", return all

    Returns:
        list: list of candles
    """
    lstReturn = []
    for entry in data:
        if entry["symbol"] == symbol and timeWindow == "ALL":
            lstReturn.append(entry)
        
        elif entry["symbol"] == symbol and \
            datetime.fromtimestamp(int(entry["time"])) <= latestdate \
                and datetime.fromtimestamp(int(entry["time"])) > \
                (latestdate - timedelta(days=timeWindow + 1)):
            lstReturn.append(entry)
    
    return lstReturn


def generateIndicators(symbol, latestdate):
    """
    Rudimentary test function to take a symbol and point in time date to acquire indicators. 
    Will serve as a helper function for runStrategy()

    Args:
        symbol (str)
        latestdate (datetime)

    Returns:
        list: list of indicator outputs
    """
    # Data extracts
    lstDaily = getDaily()
    lst1 = setTradingData(lstDaily, symbol, latestdate, 1)
    lst2 = setTradingData(lstDaily, symbol, latestdate, 2)
    lst5 = setTradingData(lstDaily, symbol, latestdate, 5)
    lst10 = setTradingData(lstDaily, symbol, latestdate, 10)
    lst20 = setTradingData(lstDaily, symbol, latestdate, 20)
    lst50 = setTradingData(lstDaily, symbol, latestdate, 50)
    lst100 = setTradingData(lstDaily, symbol, latestdate, 100)
    lst200 = setTradingData(lstDaily, symbol, latestdate, 200)
    
    lstIndicators = []

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
    print("32.8% Candle:", indicators.get328(lst1))
    print("Engulfing Candle:", indicators.getEngulfing(lst2[0], lst2[1]))
    print("Above/Below Candle:", indicators.getAboveBelow(lst2[0], lst2[1]))

    return lstIndicators


def checkGoldenCross(pricedata, latestdate):
    """
    Determines whether the short-term (20-day) exponential moving average has crossed / is crossing the
    long-term (100-day) exponential moving average in today's trade. Requires 200 days of price history in order to execute.

    Args:
        pricedata (list of candle dictionaries): 200 days of candles from a given symbol set in getStrategy
        latestdate (datetime): today for live trading, past days

    Returns:
        bool: True if crossing (buy signal) or False if not (inaction signal)
    """

    lstCandles = pricedata

    # Starting with the oldest data, iteratively check the 20-Day EMA and store in list
    lst20EMA = []
    lstWindow = lstCandles[0:20]
    intCounter = 20

    while intCounter < len(lstCandles):
        lst20EMA.append(indicators.getEMA(lstWindow, 20))
        lstWindow.pop(0)
        lstWindow.append(lstCandles[intCounter])
        intCounter += 1

    # Starting with the oldest data, iteratively check the 100-Day EMA and store in list
    lst100EMA = []
    lstWindow = lstCandles[0:100]
    intCounter = 100

    while intCounter < len(lstCandles):
        lst100EMA.append(indicators.getEMA(lstWindow, 100))
        lstWindow.pop(0)
        lstWindow.append(lstCandles[intCounter])
        intCounter += 1

    # Check last two short-term and long-term EMA calculations to see if a golden cross is occurring or not
    print(datetime.fromtimestamp(int(lstCandles[len(lstCandles)-1]["time"])))
    print("Yesterday's 20-Day EMA:", round(lst20EMA[len(lst20EMA)-2], 2))
    print("Yesterday's 100-Day EMA:", round(lst100EMA[len(lst100EMA)-2], 2))
    
    yLSD = round(lst100EMA[len(lst100EMA)-2] - lst20EMA[len(lst20EMA)-2], 2)
    
    print("Yesterday's Long/Short Delta:", yLSD)

    tLSD = round(lst100EMA[-1] - lst20EMA[-1], 2)

    print("Today's 20-Day EMA:", round(lst20EMA[-1], 2))
    print("Today's 100-Day EMA:", round(lst100EMA[-1], 2))
    print("Today's Long/Short Delta:", tLSD)

    if tLSD < yLSD:
        daysToIntersect = tLSD / (yLSD - tLSD)
        deltLSD = "Approaching, remaining days to intercept: " + str(round(daysToIntersect, 2))
    elif tLSD > yLSD:
        deltLSD = "Separating"
    elif tLSD == yLSD:
        deltLSD = "Parallel"

    print("Long/Short Delta Difference:", round(tLSD - yLSD, 2))
    print("Long/Short Directionality:", deltLSD)
    
    if lst20EMA[len(lst20EMA)-2] < lst100EMA[len(lst100EMA)-2] and lst20EMA[-1] >= lst100EMA[-1]:
        return True
    
    else:
        return False

def runStrategy(latestdate, account, params):
    """
    Called in backtest.py. params is a dictionary containing hyperparameters to test from backtest.
    Account is an object class which stores account balance and trading positions.


    Args:
        latestdate (datetime): the last day to be considered in the strategy (today for live trading, historical for backtesting)
        account (TestAccount): TestAccount instance containing balance, holdings, etc.
        params (dict): dictionary of hyperparameters for the strategy

    Returns:
        account: returns updated account object
    """
    data = getDaily()
    symbols = getSymbols()
    
    for symbol in symbols: 
        lstGoldenCross = setTradingData(data, symbol, latestdate, 100)
        
        # Runs a check for Golden Cross conditions and enters a trading position 
        if checkGoldenCross(lstGoldenCross, latestdate): # TODO: strategy to implement
            
            # Calculates the ATR for the symbol and the last 14 trading days to determine the risk / reward ratio for the trade
            floatATR = indicators.getATR(setTradingData(data, symbol, datetime.datetime.today(), 14))

            price = lstGoldenCross[0]['open'] # TODO: Build in sensitivity to buy price
            qty = 1000 / price # $1000 USD worth of whatever the symbol is on this day
                               # TODO: include balance/risk-adjusted qty's? 
            accounts.buy(symbol, price, qty, latestdate)
        
        # TODO: additional strategies (e.g., death cross)
    
    return account

print(checkGoldenCross(setTradingData(getDaily(), "SOL-USD", datetime.today(), "ALL"), datetime.today()))