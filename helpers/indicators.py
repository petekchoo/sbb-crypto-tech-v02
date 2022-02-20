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

lstDict = []
reader = csv.DictReader(open('data/test-rise.csv', mode='r', encoding='utf-8-sig'))
lstDict = list(reversed(list(reader)))

lstEMA = []
reader = csv.DictReader(open('data/test-ema.csv', mode='r', encoding='utf-8-sig'))
lstEMA = list(reader)

lstRSI = []
reader = csv.DictReader(open('data/test-rsi.csv', mode='r', encoding='utf-8-sig'))
lstRSI = list(reader)

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

'''
# Relative Strength Index: momentum indicator, current price relative to average highs / lows
def getRSI(data, timeperiod):

    # RSI function from this article: https://www.alpharithms.com/relative-strength-index-rsi-in-python-470209/

    gains = []
    losses = []

    window = []

    prev_avg_gain = None
    prev_avg_loss = None

    output = []

    for i, candle in data:

        if i == 0:
            window.append(float(candle["price"]))
            continue
        
        difference = round(float(candle["price"]) - data[i-1]["price"], 2)

        if difference > 0:
            gain = difference
            loss = 0
        
        elif difference < 0:
            gain = 0
            loss = abs(difference)
        
        else:
            gain = 0
            loss = 0

        gains.append(gain)
        losses.append(loss)

        if i < timeperiod:
            window.append(float(candle["price"]))
            continue

        if i == timeperiod:
            avg_gain = sum(gains) / len(gains)
            avg_loss = sum(losses) / len(losses)
        
        else:
            avg_gain = (prev_avg_gain * (timeperiod - 1) + gain) / timeperiod
            avg_loss = (prev_avg_loss * (timeperiod - 1) + loss) / timeperiod
        
        prev_avg_gain = avg_gain
        prev_avg_loss = avg_loss

        rs = round(avg_gain / avg_loss, 2)
        print(rs)

        rsi = round(100 - (100 / (1 + rs)), 2)
        print(rsi)

        window.append(float(candle["price"]))
        window.pop(0)
        gains.pop(0)
        losses.pop(0)
'''

print(datetime.datetime.fromtimestamp(1636761600))

# Candlestick patterns: 32.8%, engulfing, etc,

# Chart patterns: double tops, double bottoms