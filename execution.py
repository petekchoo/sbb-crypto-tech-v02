import csv, indicators, accounts, pandas, strategies
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
                (latestdate - timedelta(days=timeWindow)):
            lstReturn.append(entry)
    
    return lstReturn

def getWindowScores(params, data):
    lstScores = []
    lstEval = data[0:int(params["Pattern"])]
    intCounter = int(params["Pattern"])
    boolMatch = False

    while intCounter < len(data):
        dictCurrent = indicators.scoreMovingWindow(lstEval)
        
        for item in lstScores:
            if dictCurrent["sequence"] == item["sequence"]:
                item["strength"] += 1
                boolMatch = True

        if boolMatch == False:
            lstScores.append(dictCurrent)
        
        lstEval.append(data[intCounter])
        lstEval.pop(0)

        intCounter += 1
        boolMatch = False
    
    return lstScores

def runStrategy(candles, account, params):
    """
    Called in backtest.py. params is a dictionary containing hyperparameters to test from backtest.
    Account is an object class which stores account balance and trading positions.

    Args:
        candles (lst): the total set of data to be considered for the trading strategy ending in the current date
        account (TestAccount): TestAccount instance containing balance, holdings, etc.
        params (dict): dictionary of dates and windows relevant to executing the strategy

    Returns:
        account: returns updated account object
    """
    
    # Build a subset of data specific to the symbol and the params
    # (params are iterated by scenario and hyperparameterization)

    strSymbol = candles[-1]["symbol"]

    # Set the effective date for any open, update, or closing position
    # Note - since we are reading the closed candle for the latest day, effective trades will
    # always fall one day in the future
    dateEffective = datetime.fromtimestamp(int(candles[-1]["time"])) + timedelta(days = 1)
    
    # Next, initialize lists of data to generate indicators / strategy outputs based on the window params
    lstTrend = candles[len(candles)-int(params["Trend"])-1:len(candles) - 1]
    lstATR = candles[len(candles)-int(params["ATR"])-1:len(candles) - 1]
    lstRSI = candles[len(candles)-int(params["RSI"])-1:len(candles) - 1]

    # Set a trading price and quantity based on the midpoint of the current day's candle
    if float(candles[-1]["open"]) <= float(candles[-1]["close"]): # Price closed above open
        floatPrice = float(candles[-1]["open"]) + (float(candles[-1]["close"]) - float(candles[-1]["open"]) / 2)
    else: # Price closed below open
        floatPrice = float(candles[-1]["open"]) - (float(candles[-1]["open"]) - float(candles[-1]["close"]) / 2)

    tradeAmount = account.trade_value # Trade in increments based on account definition
    floatQuantity = tradeAmount / floatPrice # Quantity for purchase is based on the trade amount from the account
    
    # Check ATR to determine spread for position stop-loss and profit target
    floatATR = indicators.getATR(lstATR)
    
    # Set stop-loss and profit target based on ATR and targeted profit multiple
    profitMultiple = account.profit_multiple
    stopLossMultiple = account.stop_loss
    
    floatBuyStopLoss = floatPrice - (floatATR * stopLossMultiple)
    floatShortStopLoss = floatPrice + (floatATR * stopLossMultiple)
    
    floatBuyProfitTarget = floatPrice + (floatATR * profitMultiple)
    floatShortProfitTarget = floatPrice - (floatATR * profitMultiple)

    '''
    # Check for golden or death cross and buy or short accordingly
    if strategies.checkCross(candles,
                                int(params["Short EMA"]),
                                int(params["Long EMA"]))[2]["condition"] == "GOLDEN CROSS!":

        account.open_position("buy",
                        strSymbol,
                        floatPrice,
                        floatQuantity,
                        floatBuyStopLoss,
                        floatBuyProfitTarget,
                        dateEffective)

    if strategies.checkCross(candles,
                                int(params["Short EMA"]),
                                int(params["Long EMA"]))[2]["condition"] == "DEATH CROSS!":

        account.open_position("short",
                        strSymbol,
                        floatPrice,
                        floatQuantity,
                        floatShortStopLoss,
                        floatShortProfitTarget,
                        dateEffective)
    '''
    
    '''
    # Check for 7-day rising / falling trends plus corresponding RSI support
    if indicators.risingCheck(lstTrend) == True and indicators.getRSI(lstRSI, len(lstRSI)) <= 30:
        
        account.open_position("buy",
                        strSymbol,
                        floatPrice,
                        floatQuantity,
                        floatBuyStopLoss,
                        floatBuyProfitTarget,
                        dateEffective)

    elif indicators.fallingCheck(lstTrend) == True and indicators.getRSI(lstRSI, len(lstRSI)) >= 70:

        account.open_position("short",
                        strSymbol,
                        floatPrice,
                        floatQuantity,
                        floatShortStopLoss,
                        floatShortProfitTarget,
                        dateEffective)
    '''

    '''
    # TERRIBLE STRAT LOL
    # SuperTrend + EMA Support
    # Uses volatility to screen out sideways / consolidation scenarios - high risk, high reward
    if indicators.getATR(lstATR) / float(candles[-1]["close"]) > 0.1 and \
        indicators.getSuperTrend(candles)[-1] < float(candles[-1]["close"]) and \
        float(candles[-1]["low"]) <= indicators.getEMA(candles, params["Short EMA"]):

        account.open_position("buy",
                        strSymbol,
                        floatPrice,
                        floatQuantity,
                        floatBuyStopLoss,
                        floatBuyProfitTarget,
                        dateEffective)

    elif indicators.getATR(lstATR) / float(candles[-1]["close"]) > 0.1 and \
        indicators.getSuperTrend(candles)[-1] > float(candles[-1]["close"]) and \
        float(candles[-1]["high"]) >= indicators.getEMA(candles, params["Short EMA"]):

        account.open_position("short",
                        strSymbol,
                        floatPrice,
                        floatQuantity,
                        floatShortStopLoss,
                        floatShortProfitTarget,
                        dateEffective)
    '''

    # Moving window analysis of normalized patterns
     

    # Update price all existing positions, update balance with changed liability on short positions
    account.update_positions(strSymbol, floatPrice, dateEffective)

    # Close positions based on latest price and stop-loss / profit taking conditions for open positions
    account.close_positions(strSymbol, floatPrice, dateEffective)

    return account

##### Instantiation of live trading accounts & execution calls #####

##### LOCAL TESTING FOR STRATEGY FUNCTIONS #####

# NOTE: backtesting function has been moved to backtest.py