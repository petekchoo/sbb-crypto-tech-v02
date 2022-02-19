# indicators.py: functions that take in sections of dates and output a signal for
#                        the latest date (can combine with strategy.py)
#             # simple_moving_average(data, window) --> SMA
#             # exponential_moving_average(data, window) --> EMA
#             # golden_cross(data, short_window, long_window) --> signal
#             # death_cross(data, short_window, long_window) --> signal
#             # ... any other TA signals

import csv
import datetime

lstDict = []
reader = csv.DictReader(open('data/test-rise.csv', mode='r', encoding='utf-8-sig'))
lstDict = list(reversed(list(reader)))

# Basic directional: objective rising, falling based on impulsive moves and pullbacks

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

print(risingCheck(lstDict))

# Key indicators: ATR, moving averages (20, 50, 200), RSI

# Candlestick patterns: 32.8%, engulfing, 

# Chart patterns: double tops, double bottoms