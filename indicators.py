import execution

# Test code for local development, will comment out once strategy.py is set up to pass along basic
# params
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

# Key indicators: ATR, moving averages (20, 50, 200), RSI

def risingCheck(data):
    """
    Basic directional: objective rising signals based on impulsive moves and pullbacks 

    Args:
        data (list): list of candlestick dictionaries

    Returns:
        bool: if price is rising
    """
    currentLow = float(data[0]["low"])
    pullbackLow = float(data[0]["low"])
    highestHigh = float(data[0]["high"])
    boolRising = True
    for candle in data:
        # If low is lower than pullbackLow, return False
        if float(candle["low"]) < pullbackLow:
            boolRising = False
        # If low is lower than lowestCurrent and higher than pullbackLow set currentLow to low
        elif float(candle["low"]) < currentLow and float(candle["low"]) > pullbackLow:
            currentLow = float(candle["low"])
        # If high is new highest, update highestHigh and set pullbackLow to currentLow
        elif float(candle["high"]) > highestHigh:
            highestHigh = float(candle["high"])
            pullbackLow = currentLow
            currentLow = float(candle["low"])
    
    return boolRising


def fallingCheck(data):
    """
    Basic directional: objective falling signals based on impulsive moves and pullbacks 

    Args:
        data (list): list of candlestick dictionaries

    Returns:
        bool: if price is falling
    """
    # Set current high and pullback high to opening high price, and lowest low as opening low price
    currentHigh = float(data[0]["high"])
    pullbackHigh = float(data[0]["high"])
    lowestLow = float(data[0]["low"])
    
    # Set falling indicator to True by default
    boolFalling = True
    
    # Iterate through candles
    for candle in data:
        
        # If high is higher than pullbackHigh, return False
        if float(candle["high"]) > pullbackHigh:
            boolFalling = False
        
        # If high is higher than currentHigh and lower than pullbackHigh set currentHigh to high
        elif float(candle["high"]) > currentHigh and float(candle["high"]) < pullbackHigh:
            currentHigh = float(candle["high"])
        
        # If low is new lowest, update lowestLow and set pullbackHigh to currentHigh
        elif float(candle["low"]) < lowestLow:
            lowestLow = float(candle["low"])
            pullbackHigh = currentHigh
            currentHigh = float(candle["high"])
    
    return boolFalling

def getATR(data):
    """
    Average True Range - volatility indicator: average of total price spreads across the dataset 

    Args:
        data (list): list of candlestick dictionaries

    Returns:
        float: TODO
    """
    intCounter = 0
    returnATR = 0
    for candle in data:
        returnATR += (float(candle["high"]) - float(candle["low"]))
        intCounter += 1
    return (returnATR / intCounter)

def getSMA(data):
    """
    Simple Moving Average: average of closing prices across the dataset

    Args:
        data (list): list of candlestick dictionaries

    Returns:
        float: TODO
    """
    intCounter = 0
    returnAvgPrice = 0
    for candle in data:
        returnAvgPrice += float(candle["close"])
        intCounter += 1
    return (returnAvgPrice / intCounter)

 
def getEMA(data, timeperiod):
    """
    Exponential Moving Average: weighted price average that favors recency in price movement

    Args:
        data (list): list of candlestick dictionaries
        timeperiod (int): calculation window

    Returns:
        float: TODO
    """
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
        returnEMA = (float(candle["close"]) * floatMultiplier) + (returnEMA * (1 - floatMultiplier))

    return returnEMA


def getRSI(data, timeperiod):
    """
    Relative Strength Index: momentum indicator, current price relative to average highs / lows
    RSI function from this article: https://school.stockcharts.com/doku.php?id=technical_indicators:relative_strength_index_rsi
    Note: this uses a smoothing function vs. moving frame - may need to reevaluate (TODO)

    Args:
        data (list): list of candlestick dictionaries
        timeperiod (int): calculation window

    Returns:
        float: TODO
    """
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
    # If Average Loss equals zero, a “divide by zero” situation occurs for RS 
    # and RSI is set to 100 by definition. Similarly, RSI equals 0 when Average 
    # Gain equals zero.
    if avgLosses == 0: 
        RSI = 100
    else: 
        RS = avgGains / avgLosses
        RSI = 100 - (100 / (1 + RS))

    return RSI

# Trending indicator 
def getSuperTrend(candles, timeperiod=10, multiplier=3):
    '''
    Used to determine price trending direction

    Args:
        candles (lst of dicts: set of candle data
        timeperiod (int): window to examine trend data - 10 candles by default
        multiplier (int): magnitude factor for supertrend, 3 by default

    Returns:
        lstSuperTrend (lst): supertrend data for the given set of candles
    '''

    lstStart = candles[0:timeperiod + 1]
    intCounter = timeperiod + 1

    prevFinalUpper = 99999999
    prevFinalLower = -99999999
    prevSuperTrend = 0
    superTrend = prevFinalUpper

    lstSuperTrend = []

    # Iterate through the full set of candles, calculating supertrend along the way
    while intCounter < len(candles):

        floatATR = getATR(lstStart)
        
        basicUpper = ((float(lstStart[-1]["high"]) + float(lstStart[-1]["low"])) / 2) + (multiplier * floatATR)
        basicLower = ((float(lstStart[-1]["high"]) + float(lstStart[-1]["low"])) / 2) - (multiplier * floatATR)

        # Establish basic current upper band
        if basicUpper < prevFinalUpper or float(lstStart[len(lstStart) - 2]["close"]) > prevFinalUpper:
            finalUpper = basicUpper
        else:
            finalUpper = prevFinalUpper
        
        # Establish basic current lower band
        if basicLower > prevFinalLower or float(lstStart[len(lstStart) - 2]["close"]) < prevFinalLower:
            finalLower = basicLower
        else:
            finalLower = prevFinalLower
        
        # Compare to previous SuperTrend line value and current closing price to 
        if prevSuperTrend == prevFinalUpper and float(lstStart[-1]["close"]) < finalUpper:
            superTrend = finalUpper
        
        elif prevSuperTrend == prevFinalUpper and float(lstStart[-1]["close"]) > finalUpper:
            superTrend = finalLower
        
        elif prevSuperTrend == prevFinalLower and float(lstStart[-1]["close"]) > finalLower:
            superTrend = finalLower
        
        elif prevSuperTrend == prevFinalLower and float(lstStart[-1]["close"]) < finalLower:
            superTrend = finalUpper
        
        lstSuperTrend.append(superTrend)
        
        prevFinalUpper = finalUpper
        prevFinalLower = finalLower
        prevSuperTrend = superTrend

        lstStart.append(candles[intCounter])
        lstStart.pop(0)
        intCounter += 1

    return lstSuperTrend

# Function to take a set of candles, normalize the close price patterns of the candles relative
# to the set's high and low, and return a sequence pattern and a simple trading signal based
# on the pattern's final movement (if the final position is higher than the previous position, buy,
# if lower, then short, else return False for a flat signal.)
def scoreMovingWindow(candles, params):

    floatHigh = 0.00
    floatLow = 9999999999999.00

    # Iterate to find highest high and lowest low from the set:
    for candle in candles:
        if float(candle["close"]) > floatHigh:
            floatHigh = float(candle["close"])
        
        if float(candle["close"]) < floatLow:
            floatLow = float(candle["close"])

    floatIndex = (floatHigh - floatLow) / params["Scoring Range"]
    returnDict = {"sequence": [], "signal": None, "strength": 1}

    # Generate sequence
    for candle in candles:
        intScore = int(round((float(candle["close"]) - floatLow) / floatIndex, 0))
        returnDict["sequence"].append(intScore)

    # If the last score is higher than the second to last, set a buy signal
    if float(returnDict["sequence"][-1]) > float(returnDict["sequence"][-2]):
        returnDict["signal"] = "buy"
    
    # If the last score is lower than the second to last, set a short signal
    elif float(returnDict["sequence"][-1]) < float(returnDict["sequence"][-2]):
        returnDict["signal"] = "short"
    
    # If the last score is equal to the second to last, set False for hold
    else:
        returnDict["signal"] = False
    
    return returnDict

###### Candlestick patterns: 32.8%, engulfing, etc, #####

def get382(data):
    """
    32.8 Candle: hammer or inverted hammer - potential reversal indicators
    Args:
        data (list): list of candlestick dictionaries

    Returns:
        tuple (str, bool): TODO 
    """
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

def getEngulfing(oldcandle, newcandle):
    """
    Engulfing Formation: another reversal indicator
    
    Args:
        olcandle (dict):
        newcandle (dict): 

    Returns:
        tuple (str, bool): TODO 
    """
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

def getAboveBelow(oldcandle, newcandle):
    """
    Close above / below candles: reversal - indicates change in support or resistance
    
    Args:
        olcandle (dict):
        newcandle (dict): 
        
    Returns:
        tuple (str, bool): TODO 
    """
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