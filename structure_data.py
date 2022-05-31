import csv
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

def getValidSymbols(params):
    '''
    Function to test which symbols in symbols.csv have enough data history for a given set of params

    Args:
        listsymbols (lst of dicts): sourced from symbols.csv
        params (dict): set of dates and windows for a given backtesting strategy
    
    Returns:
        validSymbols (lst): list of symbols that have sufficient data for a test to be executed
    '''
    
    # Initialize a list with all candles data available per get-data and all symbols in list
    lstCandles = getDaily()
    lstSymbols = getSymbols()
    
    # Set a variable for the oldest date per the params 
    dateOldestDate = params["Current Date"] - timedelta(days = int(params["Candles"]))

    # Set a list to collect the symbols whose earliest data meets the params conditions
    lstValidSymbols = []

    # Iterate through all symbols in symbols.csv
    for symbol in lstSymbols:

        # Initialize a variable with today's date, to be updated with the oldest record for the symbol
        dateSymbolOldest = datetime.today()

        # Iterate through all candle data
        for candle in lstCandles:

            # Check for match with given symbol from symbols.csv
            if candle["symbol"] == symbol["symbol"]:

                # Check to see if the candle's date is older than dateOldest, update if so
                if datetime.fromtimestamp(int(candle["time"])) < dateSymbolOldest:
                    dateSymbolOldest = datetime.fromtimestamp(int(candle["time"]))
            
        # Check to see if the dateSymbolOldest is older than the param's earliest time period
        if dateSymbolOldest < dateOldestDate:
            lstValidSymbols.append(symbol["symbol"])
    
    return lstValidSymbols

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

def getMinute():
    """
    Read in the Daily-level file in full, build list of dictionaries

    Returns:
        list: list of candles
    """
    lstMinute = []
    reader = csv.DictReader(open('data/minute.csv', mode='r', encoding='UTF-8'))
    lstMinute = list(reader)
    return lstMinute

def getVolume():
    """
    Read in the Volume-based file in full, build list of dictionaries

    Returns:
        list: list of candles
    """
    lstVolume = []
    reader = csv.DictReader(open('data/volume.csv', mode='r', encoding='UTF-8'))
    lstVolume = list(reader)
    return lstVolume

def setTradingData(data, symbol, latestdate, timeWindow):
    """
    Build sublist of dictionaries based on a dataset, symbol/ticker, latest date, and # of days
    NOTE: potentially refactor this function to use list comprehension to be more efficient + pythonic

    Args:
        data (list): list of candles
        symbol (str): symbol to subset
        latestdate (datetime): most recent period to include
        timeWindow (int): number of periods to include, starting from latestdate, if value is "ALL", return all

    Returns:
        list: list of candles
    """
    lstReturn = []

    if timeWindow == "ALL":
        lstReturn = data.copy()
    
    else:
        lstReturn = [x for x in data if x["symbol"] == symbol and \
            datetime.fromtimestamp(int(x["time"])) <= latestdate \
                and datetime.fromtimestamp(int(x["time"])) > \
                (latestdate - timedelta(days=timeWindow))]
    
    return lstReturn