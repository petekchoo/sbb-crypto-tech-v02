import csv, indicators, volume_accounts, pandas, strategies, build_patterns
from datetime import datetime, timedelta

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
    # Note - since we are reading the closed candle for the most recent day, effective trades will
    # always fall one day in the future
    dateEffective = datetime.fromtimestamp(int(candles[-1]["time"])) + timedelta(days = 1)
    
    # Next, initialize lists of data to generate indicators / strategy outputs based on the window params
    # NOTE: only ATR is required to set pricing data, other indicators not needed for pattern modeling
    # lstTrend = candles[len(candles)-int(params["Trend"])-1:len(candles) - 1]
    # lstRSI = candles[len(candles)-int(params["RSI"])-1:len(candles) - 1]
    lstATR = candles[len(candles)-int(params["ATR"])-1:len(candles) - 1]

    # Set a trading price and quantity based on the midpoint of the current day's candle
    # NOTE: with volume candles, the spread from open to close can be substantial. Adjusting this to
    # simply be close price.
    '''
    if float(candles[-1]["open"]) <= float(candles[-1]["close"]): # Price closed above open
        floatPrice = float(candles[-1]["open"]) + (float(candles[-1]["close"]) - float(candles[-1]["open"]) / 2)
    else: # Price closed below open
        floatPrice = float(candles[-1]["open"]) - (float(candles[-1]["open"]) - float(candles[-1]["close"]) / 2)
    '''
    floatPrice = float(candles[-1]["close"])
    tradeAmount = account.trade_value # Trade in increments based on account definition
    floatQuantity = tradeAmount / floatPrice # Quantity for purchase is based on the trade amount from the account
    
    # Check ATR to determine spread for position stop-loss and profit target
    floatATR = indicators.getATR(lstATR)
    
    # Set stop-loss and profit target based on ATR and targeted profit multiple
    profitMultiple = account.profit_multiple
    stopLossMultiple = account.stop_loss
    
    # Establish profit targets and stop losses based on ATR and the multiples established in the account object
    floatBuyProfitTarget = floatPrice + (floatATR * profitMultiple)
    floatShortProfitTarget = floatPrice - (floatATR * profitMultiple)

    floatBuyStopLoss = floatPrice - (floatATR * stopLossMultiple)
    floatShortStopLoss = floatPrice + (floatATR * stopLossMultiple)

    # Read in pattern data
    reader = csv.DictReader(open(params["Pattern File"], mode='r', encoding='UTF-8'))
    lstSignals = list(reader)

    # Next, establish the current price patterns by passing the last Pattern-1 values in to be scored
    lstCheck = build_patterns.scoreMovingWindow(candles[len(candles)-params["Pattern"]:len(candles) - 1], params)
    
    # Then iterate through all signal data to see if a matching pattern exists - since all signal data
    # is pre-filtered to only be strong buy or sell signals, this enables very simple trading action
    for item in lstSignals:
        
        if item["sequence"] == str(lstCheck["sequence"]) and item["buy"] > item["short"]:
            account.open_position("buy",
                        strSymbol,
                        floatPrice,
                        floatQuantity,
                        floatShortStopLoss,
                        floatShortProfitTarget,
                        dateEffective)
        
        elif item["sequence"] == str(lstCheck["sequence"]) and item["short"] > item["buy"]:
            
            account.open_position("short",
                        strSymbol,
                        floatPrice,
                        floatQuantity,
                        floatShortStopLoss,
                        floatShortProfitTarget,
                        dateEffective)

    # Update price all existing positions, update balance with changed liability on short positions
    account.update_positions(strSymbol, floatPrice, dateEffective)

    # Close positions based on latest price and stop-loss / profit taking conditions for open positions
    account.close_positions(strSymbol, floatPrice, dateEffective)

    return account

##### Instantiation of live trading accounts & execution calls #####

##### LOCAL TESTING FOR STRATEGY FUNCTIONS #####

# NOTE: backtesting function has been moved to backtest.py

'''
# Temporarily disabling other strategies in favor of volume-based pattern matching
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