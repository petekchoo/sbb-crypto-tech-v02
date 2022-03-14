from cgi import test
import pandas as pd, numpy as np
from datetime import datetime, timedelta
from accounts import TestAccount
import execution, time

####################################
### Basic Historical Backtesting ###
####################################

# Basic backtesting function - creates a TestAccount object and calls the strategy function on it daily through all historical data
# across all currencies from the getSymbols function

def runBasicBacktest(account, symbols, params):
    '''
    Basic backtesting function that takes an account, a set of symbols, and date / window params to execute strategies
    Iterates through days of trade data until Trade End is hit

    Args:
        account (TestAccount): account object to manage trade accounting
        symbols (lst): list of symbols to take into consideration, can be initialized to getSymbols() for all
        params (dict): set of dates and windows to be used for trading date scenarios and generating indicators

    Returns:
        N/A - updates TestAccount object
    '''
    
    lstData = execution.getDaily()
    storeDate = params["Current Date"]

    for symbol in symbols:
        
        # Initialize list of candles based on symbol once per symbol
        lstCandlesSymbol = execution.setTradingData(lstData,
                                                symbol,
                                                params["Current Date"],
                                                "ALL")
        
        while params["Current Date"] < params["Trade End"]:

            # Reinitialize subset list per day to simulate moving window
            lstCandles = execution.setTradingData(lstCandlesSymbol,
                                                symbol,
                                                params["Current Date"],
                                                params["Candles"])
            
            execution.runStrategy(lstCandles, account, params)
            params["Current Date"] = params["Current Date"] + timedelta(days = 1)
        
        params["Current Date"] = storeDate

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
    lstCandles = execution.getDaily()
    lstSymbols = execution.getSymbols()
    
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

'''
    for position in accountAlpha.get_open_positions():

        print(position["symbol"])
        print(position["type"])
        print(datetime.fromtimestamp(int(position["time"])))

        if position["type"] == "buy":
            print("Position value at close:", (float(position["close_price"])-float(position["init_price"])) * float(position["quantity"]))
        
        elif position["type"] == "short":
            print("Position value at close:", (float(position["init_price"])-float(position["close_price"])) * float(position["quantity"]))
        
        print()
'''

##############################
### Define scenarios here ####
##############################

scenarios = [] # container for all the scenarios defined below

# Last month of data
scenario = {
    'name': 'recent 30 days',
    'start': datetime(2022, 1, 21, 23, 59, 59),
    'end': datetime(2022, 2, 20, 23, 59, 59)
}
scenarios.append(scenario)

# Bitcoin cash fork: June 30 2017 - August 31 2017
scenario = {
    'name': 'bitcoin cash hard fork',
    'start': datetime(2017, 6, 30, 23, 59, 59),
    'end': datetime(2017, 8, 31, 23, 59, 59)
}
scenarios.append(scenario)

# China regulation: August 10, 2017 - September 20, 2017
scenario = {
    'name': 'china 2017 regulation',
    'start': datetime(2017, 8, 10, 23, 59, 59),
    'end': datetime(2017, 9, 20, 23, 59, 59)
}
scenarios.append(scenario)

# Bitcoin crash: December 2017
scenario = {
    'name': 'bitcoin december 2017 crash',
    'start': datetime(2017, 12, 1, 23, 59, 59),
    'end': datetime(2017, 12, 31, 23, 59, 59)
}
scenarios.append(scenario)

# Ethereum decline: January 2018 - April 2018
scenario = {
    'name': 'bitcoin cash hard fork',
    'start': datetime(2018, 1, 1, 23, 59, 59),
    'end': datetime(2018, 4, 30, 23, 59, 59)
}
scenarios.append(scenario)

# December 2017-December 2018
"""
2017 was a landmark year for Bitcoin, which broke all its own records and peaked near $20,000. 
Then, on Dec. 27, it all came crashing down as investors harvested gains from what was an obvious 
bubble and sent the price cratering below $12,000. The cryptocurrency would remain in the doldrums 
throughout 2018, as major hacks in Korea and Japan — as well as rumors that those countries were 
planning to ban Bitcoin — sent already skittish investors looking for the exits.

source: https://www.yahoo.com/video/7-biggest-bitcoin-crashes-history-180038282.html
"""
scenario = {
    'name': '2018 doldrums',
    'start': datetime(2017, 12, 1),
    'end': datetime(2018, 12, 31)
}
scenarios.append(scenario)

# March 2020: -50%
"""
The pandemic did not spare Bitcoin, and when the markets crashed in March 2020, the Bitcoin 
market crashed even harder. Bitcoin lost half its value in two days. Over a month, it fell 
from above $10,000 in February to below $4,000 in March.

source: https://www.yahoo.com/video/7-biggest-bitcoin-crashes-history-180038282.html
"""
scenario = {
    'name': 'March 2020 pandemic',
    'start': datetime(2020, 3, 1),
    'end': datetime(2020, 3, 31)
}
scenarios.append(scenario)

# May 2021: -53%
"""
In April, Bitcoin was the talk of the investing world as it roared past an astonishing 
$64,000 for a single coin. Then, in a flash, $1 trillion in value was wiped off the global 
crypto market in a single week. First, Elon Musk went back on a promise to accept Bitcoin 
as a payment for Tesla cars. Then, China announced yet another crypto crackdown. Finally, 
the public learned about the environmental impact of Bitcoin mining and crypto investors 
found themselves in a familiar position — at the mercy of forces beyond their control.

source: https://www.yahoo.com/video/7-biggest-bitcoin-crashes-history-180038282.html
"""
scenario = {
    'name': 'May 2021 volatility',
    'start': datetime(2021, 5, 1),
    'end': datetime(2021, 5, 31)
}
scenarios.append(scenario)

#### SCENARIO BASED TESTING

testParams = {"Trade Start": datetime(2021, 3, 6, 23, 59, 59),
                "Current Date": datetime(2021, 3, 6, 23, 59, 59),
                "Trade End": datetime(2022, 3, 6, 23, 59, 59),
                "Candles": 210,
                "Trend": 5,
                "Pattern": 14,
                "ATR": 14,
                "Short EMA": 20,
                "Long EMA": 200,
                "RSI": 14}


accountAlpha = TestAccount(balance = 5000, profit = 3, stoploss = 1.5)
testSymbols = getValidSymbols(testParams)
runBasicBacktest(accountAlpha, testSymbols, testParams)

#  ACCOUNT SUMMARY OUTPUT
print()
print("Total Positions:", len(accountAlpha.open_positions))
print("Final Account Balance:", accountAlpha.balance)
print("Maximum Account Drawdown:", accountAlpha.max_drawdown)
print()

#   POSITION SUMMARY BY TYPE

floatBuyTotal = 0.00
floatShortTotal = 0.00
floatOpenBuyTotal = 0.00
floatOpenShortTotal = 0.00

for position in accountAlpha.open_positions:
    
    if position["status"] == False:
    
        if position["type"] == "buy":
            floatBuyTotal += (float(position["close_price"]) - float(position["init_price"])) * float(position["quantity"])
        
        elif position["type"] == "short":
            floatShortTotal += (float(position["init_price"]) - float(position["close_price"])) * float(position["quantity"])

    else:
        
        if position["type"] == "buy":
            floatOpenBuyTotal += (float(position["current_price"]) - float(position["init_price"])) * float(position["quantity"])
        
        else:
            floatOpenShortTotal += (float(position["init_price"]) - float(position["current_price"])) * float(position["quantity"])

print("Closed buy value:", floatBuyTotal)
print("Closed short value:", floatShortTotal)
print("Open (unrealized) buy value:", floatOpenBuyTotal)
print("Open (unrealized) short value:", floatOpenShortTotal)
print()

''' POSITION REVIEW
for position in accountAlpha.open_positions:
    print("Position opened on:", position["time"])
    print("Position closed on:", position["close_time"])
    print("Symbol:", position["symbol"])
    print("Order type:", position["type"])
    print("Open price:", position["init_price"])
    print("Close price:", position["close_price"])
    
    if position["status"] == False:

        if position["type"] == "buy":
            print("% value increase:", (float(position["close_price"]) - float(position["init_price"])) / float(position["init_price"]))
            print("Position value at close:", (float(position["close_price"]) - float(position["init_price"])) * position["quantity"])
        
        else:
            print("% value increase:", (float(position["init_price"]) - float(position["close_price"])) / float(position["init_price"]))
            print("Position value at close:", (float(position["init_price"]) - float(position["close_price"])) * position["quantity"])
        print()
    
    else:
        print("Open position price:", float(position["current_price"]))
        print("Open position quantity:", float(position["quantity"]))
        print("Open position value:", float(position["current_price"]) * float(position["quantity"]))
        print()
'''

'''
# TEST ALL SCENARIOS
for scenarioX in scenarios:

    accountAlpha = TestAccount(balance = 5000, profit = 3, stoploss = 1.5)
    
    testParams["Trade Start"] = scenarioX["start"]
    testParams["Current Date"] = testParams["Trade Start"]
    testParams["Trade End"] = scenarioX["end"]

    testSymbols = getValidSymbols(testParams)

    runBasicBacktest(accountAlpha, testSymbols, testParams)
    
    print(scenarioX["name"])
    print("Total Positions:", len(accountAlpha.open_positions))
    print("Final Account Balance:", accountAlpha.balance)
    print("Profit / Loss:", accountAlpha.balance - 5000)
    print("Maximum Account Drawdown:", accountAlpha.max_drawdown)
    print()
'''

##############################
### Hyperparameter tuning ####
##############################

'''TEMPORARILY DISABLING UNTIL BASIC BACKTESTING IS FUNCTIONAL
# Hyperparameter Tuning functions

def getSize(paramGrid):
    keys, valuesList = zip(*sorted(paramGrid.items())[::-1])
    sizes = [len(vList) for vList in valuesList]
    total = np.product(sizes)
    return total 

def getItem(paramGrid, ind):
    """
    Get the parameters that would be ``ind``th in iteration
    Parameters
    ----------
    ind : int
        The iteration index
    Returns
    -------
    params : dict of str to any
        Equal to list(self)[ind]
    
    Reference: https://github.com/scikit-learn/ \
            scikit-learn/blob/7e1e6d09bcc2eaeba98 \
            f7e737aac2ac782f0e5f1/sklearn/model_selection/_search.py
    """
    # This is used to make discrete sampling without replacement memory
    # efficient.
    paramGrid = [paramGrid]
    for subGrid in paramGrid:
        # XXX: could memoize information used here
        if not subGrid:
            if ind == 0:
                return {}
            else:
                ind -= 1
                continue

        # Reverse so most frequent cycling parameter comes first
        keys, valuesList = zip(*sorted(subGrid.items())[::-1])
        sizes = [len(vList) for vList in valuesList]
        total = np.product(sizes)

        if ind >= total:
            # Try the next grid
            ind -= total
        else:
            out = {}
            for key, vList, n in zip(keys, valuesList, sizes):
                ind, offset = divmod(ind, n)
                out[key] = vList[offset]
            return out

    raise IndexError("ParameterGrid index out of range")

### DEFINE THIS ###
paramGrid = {
    'shortWindow': np.arange(10, 55, 5),
    'longWindow': np.arange(50, 505, 25),
    'emaTimePeriod': np.arange(12, 202, 2),
}       

# Run GridSearch on paramGrid
bestScore = 0
bestParams = None
granularity = 86400
for i in range(getSize(paramGrid)):
    # Fixed parameters
    startingBalance = 5000
    account = TestAccount(startingBalance)
    currScore = startingBalance
    currParams = getItem(paramGrid, i)

    # Hyperparameter tuning dates: June 1, 2021 - Jan 20, 2022
    start = datetime(2021, 6, 1).timestamp()
    end = datetime(2022, 1, 20).timestamp()

    curr = start
    while end < curr:
        account = strategy.runStrategy(datetime.fromtimestamp(curr), account, currParams) # TODO: make this the interface for runStrategy
        curr += granularity
        if account.balance < 0.2 * startingBalance: 
            break
    
    currScore = account.balance # Scoring function is absolute returns
    if currScore > bestScore:
        bestParams = currParams

print('Best Params:', bestParams)
'''

### RUN THIS SECTION AFTER BEST PARAMS HAS BEEN CONFIGURED ###

# ##############################
# ###  Backtesting results  ####
# ##############################


# # Configure this based on hyperparameter tuning results
# bestParams = {
#     'shortWindow': 50,
#     'longWindow': 500,
#     'emaTimePeriod': 200,
# }       

# # data = pd.read_csv('data/daily.csv', index_col=None)
# # symbols = data['symbol'].unique()

# for scenario in scenarios:
#     # Scenario parameters
#     startingBalance = 5000
#     backtestAccount = TestAccount(startingBalance)

#     # Metrics to keep track of during backtest
#     maxDrawdown = 0
#     countTrades = 0
#     returnArray = [] # to calculate volatility of returns
#     endingBalance = 0

#     name = scenario['name'] 
#     start = scenario['start']
#     end = scenario['end']
    
#     curr = start
#     while end < curr:
#         account = strategy.runStrategy(datetime.fromtimestamp(curr), account, currParams) # TODO: make this the interface for runStrategy
#         curr += granularity
#         if account.balance < 0.2 * startingBalance: 
#             break
