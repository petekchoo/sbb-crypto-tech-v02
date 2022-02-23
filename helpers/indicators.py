# indicators.py: functions that take in sections of dates and output a signal for
#                        the latest date (can combine with strategy.py)
#             # simple_moving_average(data, window) --> SMA
#             # exponential_moving_average(data, window) --> EMA
#             # golden_cross(data, short_window, long_window) --> signal
#             # death_cross(data, short_window, long_window) --> signal
#             # ... any other TA signals

# Test code for local development, will comment out once strategy.py is set up to pass along basic
# params

import csv
import datetime

'''
lstDict = []
reader = csv.DictReader(open('data/test-rise.csv', mode='r', encoding='utf-8-sig'))
lstDict = list(reversed(list(reader)))

lstEMA = []
reader = csv.DictReader(open('data/test-ema.csv', mode='r', encoding='utf-8-sig'))
lstEMA = list(reader)

lstRSI = [{'open':'44.34', 'close':'44.09'},
        {'open':'44.09', 'close':'44.15'},
        {'open':'44.15', 'close':'43.61'},
        {'open':'43.61', 'close':'44.33'},
        {'open':'44.33', 'close':'44.83'},
        {'open':'44.83', 'close':'45.10'},
        {'open':'45.10', 'close':'45.42'},
        {'open':'45.42', 'close':'45.84'},
        {'open':'45.84', 'close':'46.08'},
        {'open':'46.08', 'close':'45.89'},
        {'open':'45.89', 'close':'46.03'},
        {'open':'46.03', 'close':'45.61'},
        {'open':'45.61', 'close':'46.28'},
        {'open':'46.28', 'close':'46.28'},
        ]
'''

# Basic directional: objective rising & falling signals based on impulsive moves and pullbacks

def risingCheck(data):

    currentLow = float(data[0]["low"])
    pullbackLow = float(data[0]["low"])
    
    highestHigh = float(data[0]["high"])
    boolRising = True

    for candle in data:
        
        # If low is lower than pullbackLow, return False
        if float(candle["low"]) < pullbackLow:
            boolRising = False

        # If low is lower than lowestCurrent and higher than pullbackLow
        #   set currentLow to low
        elif float(candle["low"]) < currentLow and float(candle["low"]) > pullbackLow:
            currentLow = float(candle["low"])
        
        # If high is new highest, update highestHigh and set pullbackLow to currentLow
        elif float(candle["high"]) > highestHigh:
            highestHigh = float(candle["high"])
            pullbackLow = currentLow
            currentLow = float(candle["low"])

    return boolRising

def fallingCheck(data):

    currentHigh = float(data[0]["low"])
    pullbackHigh = float(data[0]["low"])
    
    lowestLow = float(data[0]["high"])
    boolFalling = True

    for candle in data:
        
        # If high is higher than pullbackHigh, return False
        if float(candle["high"]) > pullbackHigh:
            boolFalling = False

        # If high is higher than lowestCurrent and lower than pullbackHigh
        #   set currentHigh to high
        elif float(candle["high"]) > currentHigh and float(candle["high"]) < pullbackHigh:
            currentHigh = float(candle["high"])
        
        # If low is new lowest, update lowestLow and set pullbackHigh to currentHigh
        elif float(candle["low"]) < lowestLow:
            lowestLow = float(candle["low"])
            pullbackHigh = currentHigh
            currentHigh = float(candle["high"])

    return boolFalling

# Key indicators: ATR, moving averages (20, 50, 200), RSI

# Average True Range - volatility indicator: average of total price spreads across the dataset
def getATR(data):

    intCounter = 0
    returnATR = 0

    for candle in data:
        returnATR += (float(candle["high"]) - float(candle["low"]))
        intCounter += 1
    
    return (returnATR / intCounter)

# Simple Moving Average: average of closing prices across the dataset
def getSMA(data):

    intCounter = 0
    returnAvgPrice = 0

    for candle in data:
        returnAvgPrice += float(candle["close"])
        intCounter += 1
    
    return (returnAvgPrice / intCounter)

# Exponential Moving Average: weighted price average that favors recency in price movement
def getEMA(data, timeperiod):
    
    lstSMA = []
    lstEMA = []

    # Separate data into initial SMA and subsequent EMA calculation window based on timeperiod
    for i in range(0, timeperiod):
        lstSMA.append(data[i])
    
    for i in range(timeperiod, len(data)):
        lstEMA.append(data[i])

    # Calculate SMA for initial EMA based 
    returnEMA = getSMA(lstSMA)
    
    # Calculate weighting based on timeperiod
    floatMultiplier = (2 / (timeperiod + 1))

    # For loop to calculate the exponential moving average
    for candle in lstEMA:
        returnEMA = (float(candle["close"]) - returnEMA) * floatMultiplier + returnEMA

    return returnEMA

# Relative Strength Index: momentum indicator, current price relative to average highs / lows
def getRSI(data, timeperiod):

    # RSI function from this article: https://school.stockcharts.com/doku.php?id=technical_indicators:relative_strength_index_rsi
    # Note this uses a smoothing function vs. moving frame - may need to reevaluate

    lstInit = []
    lstRSI = []
    lstGains = []
    lstLosses = []

    avgGains = None
    avgLosses = None
    RS = None
    RSI = None

    # Separate data into initial and subsequent calculation window based on timeperiod
    for i in range(0, timeperiod):
        lstInit.append(data[i])
    
    for i in range(timeperiod, len(data)):
        lstRSI.append(data[i])

    # Calculate average gains and losses for initial period
    for candle in lstInit:
        # Check if gain or loss, add to appropriate list
        if float(candle["open"]) < float(candle["close"]):
            lstGains.append(float(candle["close"])-float(candle["open"]))
        else:
            lstLosses.append(float(candle["open"])-float(candle["close"]))
    
    avgGains = sum(lstGains) / timeperiod
    avgLosses = sum(lstLosses) / timeperiod

    # For loop to update avgGains, avgLosses on remaining values
    for candle in lstRSI:
        if float(candle["open"]) < float(candle["close"]):
            avgGains = ((avgGains * (timeperiod - 1)) + \
                (float(candle["close"])-float(candle["open"]))) \
                    / timeperiod
        else:
            avgLosses = ((avgLosses * (timeperiod - 1)) + \
                (float(candle["open"])-float(candle["close"]))) \
                    / timeperiod

    # Calculate final RS, RSI
    RS = avgGains / avgLosses
    RSI = 100 - (100 / (1 + RS))

    return RSI

# Candlestick patterns: 32.8%, engulfing, etc,

# 32.8 Candle: hammer or inverted hammer - potential reversal indicators
def get382(data):
    
    for candle in data:
        # Check for bullish scenario, else check bearish scenario
        if float(candle["close"]) > float(candle["open"]):
            
            # If entire candle falls within 38.2% Fibonnaci retracement, return True, else False
            if float(candle["open"]) > \
                float(candle["high"]) - ((float(candle["high"]) - float(candle["low"])) * 0.382):
                return "Bullish", True
            
            else:
                return "Bullish", False
        else:
            if float(candle["open"]) < \
                float(candle["low"]) + ((float(candle["high"]) - float(candle["low"])) * 0.382):
                return "Bearish", True
            
            else:
                return "Bearish", False

# Engulfing Formation: another reversal indicator
def getEngulfing(oldcandle, newcandle):

    # Check for bearish scenario
    if float(oldcandle["close"]) > float(oldcandle["open"]) \
        and float(newcandle["open"]) > float(newcandle["close"]):

        # Check engulfing
        if float(newcandle["open"]) > float(oldcandle["close"]) \
            and float(newcandle["close"]) < float(oldcandle["open"]):

            return "Bearish", True
        
        else:
            return "Bearish", False
    
    # Check for bullish scenario
    elif float(oldcandle["open"]) > float(oldcandle["close"]) \
        and float(newcandle["close"]) > float(newcandle["open"]):

        # Check engulfing
        if float(newcandle["close"]) > float(oldcandle["open"]) \
            and float(newcandle["open"]) < float(oldcandle["close"]):

            return "Bullish", True
        
        else:
            return "Bullish", False
    
    # If both candles are bearish or bullish, not an engulfing scenario
    else:
        return "Non-Engulfing"

# Close above / below candles: reversal - indicates change in support or resistance

def getAboveBelow(oldcandle, newcandle):

    # Check for bearish scenario
    if float(oldcandle["close"]) > float(oldcandle["open"]) \
        and float(newcandle["open"]) > float(newcandle["close"]):

        # Check close below
        if float(newcandle["close"]) < float(oldcandle["low"]):

            return "Bearish, Close Below", True
        
        else:
            return "Bearish", False
    
    # Check for bullish scenario
    elif float(oldcandle["open"]) > float(oldcandle["close"]) \
        and float(newcandle["close"]) > float(newcandle["open"]):

        # Check close above
        if float(newcandle["close"]) > float(oldcandle["high"]):

            return "Bullish, Close Above", True
        
        else:
            return "Bullish", False
    
    # If both candles are bearish or bullish, not an engulfins scenario
    else:
        return "Not Above / Below"

# print(getAboveBelow({"open":"50", "close": "30", "high": "50", "low": 10}, \
#   {"open":"10", "close": "49", "high": "30", "low": 50}))

# Chart patterns: double tops, double bottoms