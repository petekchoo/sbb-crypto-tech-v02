import pandas as pd, numpy as np
from datetime import datetime
from account import TestAccount
import strategy


##############################
### Define scenarios here ####
##############################

scenarios = [] # container for all the scenarios defined below

# Last month of data
scenario = {
    'name': 'recent 30 days',
    'start': datetime(2022, 1, 21),
    'end': datetime(2022, 2, 20)
}
scenarios.append(scenario)

# Bitcoin cash fork: June 30 2017 - August 31 2017
scenario = {
    'name': 'bitcoin cash hard fork',
    'start': datetime(2017, 6, 30),
    'end': datetime(2017, 8, 31)
}
scenarios.append(scenario)

# China regulation: August 10, 2017 - September 20, 2017
scenario = {
    'name': 'china 2017 regulation',
    'start': datetime(2017, 8, 10),
    'end': datetime(2017, 9, 20)
}
scenarios.append(scenario)

# Bitcoin crash: December 2017
scenario = {
    'name': 'bitcoin december 2017 crash',
    'start': datetime(2017, 12, 1),
    'end': datetime(2017, 12, 31)
}
scenarios.append(scenario)

# Ethereum decline: January 2018 - April 2018
scenario = {
    'name': 'bitcoin cash hard fork',
    'start': datetime(2018, 1, 1),
    'end': datetime(2018, 4, 30)
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


##############################
### Hyperparameter tuning ####
##############################

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
