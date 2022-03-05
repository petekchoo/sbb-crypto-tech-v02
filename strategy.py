import csv, indicators, accounts, pandas
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

def checkCross(pricedata):
    """
    Looks for golden and death cross scenarios based on 20-day and 100-day EMAs, specifically seeking a cross event in the last two candles

    Args:
        pricedata (list of candle dictionaries): 200 days of candles from a given symbol set in getStrategy

    Returns:
        list: list of three dictionaries that contain yesterday's and today's short- and long-term EMAs, the cross condition, and
                distance to intercept if relevant (else None)
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

    # Set variables for evaluating cross checks
    yesterday20EMA = lst20EMA[len(lst20EMA)-2]
    yesterday100EMA = lst100EMA[len(lst100EMA)-2]
    today20EMA = lst20EMA[-1]
    today100EMA = lst100EMA[-1]
    
    yestLongShortDistance = abs(yesterday20EMA - yesterday100EMA)
    todayLongShortDistance = abs(today20EMA - today100EMA)

    strCondition = ""
    floatInterceptDays = None
    
    # Store variables in a list of dictionaries that can be appended and analyzed by the strategy / backtesting functions
    # Each list contains three dicts: yesterday's long- and short-term EMA, today's long- and short-term EMA, and the latest
    # cross 'condition' and days to intercept on current trajectory.
    lstDictData = [{"day1short": yesterday20EMA,
                    "day1long": yesterday100EMA},
                    {"day2short": today20EMA,
                    "day2long": today100EMA},
                    {"condition": strCondition,
                    "intercept": floatInterceptDays}]

    # PLACEHOLDER for function to extrapolate the X day intercept of the short- and long-term EMAs using linear regression.

    # Determine golden vs. death, if long/short gap is closing or expanding - if closing, project intersect (simple linear)
    if yesterday20EMA > yesterday100EMA and today20EMA > today100EMA: # Short-term is above long-term yesterday and today
        if yestLongShortDistance > todayLongShortDistance: # Short-term approaching long-term from above
            lstDictData[2]["condition"] = "Short-term approaching long-term from above"
            lstDictData[2]["intercept"] = round(todayLongShortDistance/(yestLongShortDistance-todayLongShortDistance), 2)

            return lstDictData
        
        elif yestLongShortDistance < todayLongShortDistance: # Short-term moving away from long-term from above
            lstDictData[2]["condition"] = "Short-term rising further above long-term"
            lstDictData[2]["intercept"] = None

            return lstDictData
    
    elif yesterday20EMA < yesterday100EMA and today20EMA < today100EMA: # Short-term is below long-term yesterday and today
        if yestLongShortDistance > todayLongShortDistance: # Short-term approaching long-term from below
            lstDictData[2]["condition"] = "Short-term approaching long-term from below"
            lstDictData[2]["intercept"] = round(todayLongShortDistance/(yestLongShortDistance-todayLongShortDistance), 2)

            return lstDictData
        
        elif yestLongShortDistance < todayLongShortDistance: # Short-term moving away from long-term from below
            lstDictData[2]["condition"] = "Short-term sinking lower below long-term"
            lstDictData[2]["intercept"] = None

            return lstDictData
    
    elif yesterday20EMA > yesterday100EMA and today20EMA <= today100EMA: # Death cross occurring today
        lstDictData[2]["condition"] = "DEATH CROSS!"
        lstDictData[2]["intercept"] = None

        return lstDictData
    
    elif yesterday20EMA < yesterday100EMA and today20EMA >= today100EMA: # Golden cross occurring today
        lstDictData[2]["condition"] = "GOLDEN CROSS!"
        lstDictData[2]["intercept"] = None

        return lstDictData

def runStrategy(lstCandles, account, params):
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
    
    # Build a subset of data specific to the symbol
    intWindow = 14

    # Check ATR to determine spread for trade
    floatATR = indicators.getATR(lstCandles)
    
    # Set a trading price and quantity based on the midpoint of the current day's candle
    if float(lstCandles[-1]["open"]) <= float(lstCandles[-1]["close"]): # Price closed above open
        floatPrice = float(lstCandles[-1]["open"]) + ((float(lstCandles[-1]["close"]) - float(lstCandles[-1]["open"])/2))
    else: # Price closed below open
        floatPrice = float(lstCandles[-1]["open"]) - ((float(lstCandles[-1]["open"]) - float(lstCandles[-1]["close"])/2))

    tradeAmount = 10 # Trade in $10 increments
    floatQuantity = tradeAmount / floatPrice # Quantity is $10 worth of given symbol on the date (midpoint price)
    
    # Set stop-loss and profit target based on ATR and targeted profit multiple
    profitMultiple = 2.0
    floatStopLoss = floatPrice - floatATR
    floatProfitTarget = floatPrice + (floatATR * profitMultiple)

    # Check for 14-day rising / falling trends plus corresponding RSI support
    # Note: using wider than standard RSI bands to drive higher trading activity for testing
    if indicators.risingCheck(lstCandles) == True and indicators.getRSI(lstCandles, intWindow) <= 50:
        
        print("Buying!")
        # Bullish stop-loss set 1x ATR below, profit target set 2x ATR above the trading price
        floatStopLoss = floatPrice - floatATR
        floatProfitTarget = floatPrice + (floatATR * profitMultiple)
        
        account.trade("buy",
                        lstCandles[-1]["symbol"],
                        floatPrice,
                        floatQuantity,
                        floatStopLoss,
                        floatProfitTarget,
                        lstCandles[-1]["time"])

    elif indicators.fallingCheck(lstCandles) == True and indicators.getRSI(lstCandles, intWindow) >= 50:
        
        # Bearish stop-loss set 1x ATR above, profit target set 2x ATR below the trading price
        floatStopLoss = floatPrice + floatATR
        floatProfitTarget = floatPrice - (floatATR * profitMultiple)

        account.trade("short",
                        lstCandles[-1]["symbol"],
                        floatPrice,
                        floatQuantity,
                        floatStopLoss,
                        floatProfitTarget,
                        lstCandles[-1]["time"])
    
    # TODO: write check position logic to exit positions based on stop-loss and profit targets of open positions
    
    return account

##### LOCAL TESTING FOR STRATEGY FUNCTIONS #####

lstSymbols = getSymbols()
intGoldenCrosses = 0

# TEST: Iterates through all symbols starting 200 days after the earliest available data (needed to set initial EMA window)
#       Checks for golden and death cross conditions every day after day 200.
#       Since checkCross compares the previous day's averages to today's, the function returns a tuple with both days' data
#       that can be stored for modeling / visualization purposes later.

lstTest = setTradingData(getDaily(), "BTC-USD", datetime.today(), "ALL")
lstStart = lstTest[0:15]
intCounter = 15
accountAlpha = accounts.TestAccount()

while intCounter < len(lstTest):

    ''' Crosses unit testing
    if checkCross(lstStart)[2]["condition"] == "DEATH CROSS!":
        print(datetime.fromtimestamp(int(lstStart[-1]["time"])))
        print(checkCross(lstStart))
        print()
    '''
    
    ''' Rising / falling + RSI unit testing
    if indicators.risingCheck(lstStart) == True and indicators.getRSI(lstStart, 7) <= 50:
        print("Bought on:", datetime.fromtimestamp(int(lstStart[-1]["time"])))
    
    elif indicators.fallingCheck(lstStart) == True and indicators.getRSI(lstStart, 14) >= 50:
        print("Shorted on:", datetime.fromtimestamp(int(lstStart[-1]["time"])))
    '''
    
    # Test account trading function throughout history
    
    runStrategy(lstStart, accountAlpha, None)

    # Iteration logic for "moving window"
    lstStart.append(lstTest[intCounter])
    lstStart.pop(0)
    intCounter += 1

for position in accountAlpha.get_open_positions():
    print(position)
    print()

###### GRAVEYARD: Deprecated or retired functions #######

'''
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
'''