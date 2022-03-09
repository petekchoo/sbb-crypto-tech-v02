import csv, indicators, accounts, pandas

from numpy import short
from datetime import datetime, timedelta

# Strategies to be called from execution.py as part of the trading strategy
# Abstracted out of execution.py to enable easier adjustment of core strategy execution
# in backtesting and live trading

def checkCross(candles, shortwindow, longwindow):
    """
    Looks for golden and death cross scenarios based on 20-day and 100-day EMAs, specifically seeking a cross event in the last two candles

    Args:
        pricedata (list of candle dictionaries): 200 days of candles from a given symbol set in getStrategy

    Returns:
        list: list of three dictionaries that contain yesterday's and today's short- and long-term EMAs, the cross condition, and
                distance to intercept if relevant (else None)
    """

    # Starting with the oldest data, iteratively check the 20-Day EMA and store in list
    lstShortEMA = []
    lstWindow = candles[0:shortwindow]
    intCounter = shortwindow

    while intCounter < len(candles):
        lstShortEMA.append(indicators.getEMA(lstWindow, shortwindow))
        lstWindow.pop(0)
        lstWindow.append(candles[intCounter])
        intCounter += 1

    # Starting with the oldest data, iteratively check the 100-Day EMA and store in list
    lstLongEMA = []
    lstWindow = candles[0:longwindow]
    intCounter = longwindow

    while intCounter < len(candles):
        lstLongEMA.append(indicators.getEMA(lstWindow, longwindow))
        lstWindow.pop(0)
        lstWindow.append(candles[intCounter])
        intCounter += 1

    # Set variables for evaluating cross checks
    yesterdayShortEMA = lstShortEMA[len(lstShortEMA)-2]
    yesterdayLongEMA = lstLongEMA[len(lstLongEMA)-2]
    todayShortEMA = lstShortEMA[-1]
    todayLongEMA = lstLongEMA[-1]
    
    yestLongShortDistance = abs(yesterdayShortEMA - yesterdayLongEMA)
    todayLongShortDistance = abs(todayShortEMA - todayLongEMA)

    strCondition = ""
    floatInterceptDays = None
    
    # Store variables in a list of dictionaries that can be appended and analyzed by the strategy / backtesting functions
    # Each list contains three dicts: yesterday's long- and short-term EMA, today's long- and short-term EMA, and the latest
    # cross 'condition' and days to intercept on current trajectory.
    lstDictData = [{"day1short": yesterdayShortEMA,
                    "day1long": yesterdayLongEMA},
                    {"day2short": todayShortEMA,
                    "day2long": todayLongEMA},
                    {"condition": strCondition,
                    "intercept": floatInterceptDays}]

    # PLACEHOLDER for function to extrapolate the X day intercept of the short- and long-term EMAs using linear regression.

    # Determine golden vs. death, if long/short gap is closing or expanding - if closing, project intersect (simple linear)
    if yesterdayShortEMA >= yesterdayLongEMA and todayShortEMA >= todayLongEMA: # Short-term is above long-term yesterday and today
        if yestLongShortDistance >= todayLongShortDistance: # Short-term approaching long-term from above
            lstDictData[2]["condition"] = "Short-term approaching long-term from above"
            #lstDictData[2]["intercept"] = round(todayLongShortDistance/(yestLongShortDistance-todayLongShortDistance), 2)

            return lstDictData
        
        elif yestLongShortDistance < todayLongShortDistance: # Short-term moving away from long-term from above
            lstDictData[2]["condition"] = "Short-term rising further above long-term"
            lstDictData[2]["intercept"] = None

            return lstDictData
    
    elif yesterdayShortEMA < yesterdayLongEMA and todayShortEMA < todayLongEMA: # Short-term is below long-term yesterday and today
        if yestLongShortDistance >= todayLongShortDistance: # Short-term approaching long-term from below
            lstDictData[2]["condition"] = "Short-term approaching long-term from below"
            #lstDictData[2]["intercept"] = round(todayLongShortDistance/(yestLongShortDistance-todayLongShortDistance), 2)

            return lstDictData
        
        elif yestLongShortDistance < todayLongShortDistance: # Short-term moving away from long-term from below
            lstDictData[2]["condition"] = "Short-term sinking lower below long-term"
            lstDictData[2]["intercept"] = None

            return lstDictData
    
    elif yesterdayShortEMA > yesterdayLongEMA and todayShortEMA <= todayLongEMA: # Death cross occurring today
        lstDictData[2]["condition"] = "DEATH CROSS!"
        lstDictData[2]["intercept"] = None

        return lstDictData
    
    elif yesterdayShortEMA < yesterdayLongEMA and todayShortEMA >= todayLongEMA: # Golden cross occurring today
        lstDictData[2]["condition"] = "GOLDEN CROSS!"
        lstDictData[2]["intercept"] = None

        return lstDictData


