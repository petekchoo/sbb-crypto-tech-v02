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

lstBTC = []

for candle in lstMinute:
    if candle["symbol"] == "BTC-USD":
        lstBTC.append(candle)

keys = lstBTC[0].keys()

a_file = open("data/testBTC.csv", "w")
dict_writer = csv.DictWriter(a_file, keys)
dict_writer.writeheader()
dict_writer.writerows(lstBTC)
a_file.close()

'''