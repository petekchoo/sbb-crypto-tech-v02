import structure_data, indicators, csv, datetime

# Building a function (TBD module) to build out and store trading patterns.

lstSymbols = structure_data.getSymbols()
lstVolume = structure_data.getVolume()

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

# Takes a list of candle dictionary objects and a params object to build a list of
# patterns with associated trading signals
def getWindowScores(candles, patterns, params):
    
    # Initialize variables, including an empty list of patterns, the starting pattern to
    # evaluate, a working counter to iterate through the list of candles, and a matching boolean
    lstPatterns = patterns
    lstEval = candles[0:int(params["Pattern"])]
    intCounter = int(params["Pattern"])
    boolMatch = False

    # Iterate through the list of candles
    while intCounter < len(candles):
        
        # Initialize a dict object using the moving window function based on the initial Eval object
        dictCurrent = scoreMovingWindow(lstEval, params)
        
        # Check the list of patterns to see if the sequence has already been logged
        for item in lstPatterns:
            
            # If so, increment the sequence's 'strength' in the pattern list and set the match boolean to True
            if dictCurrent["sequence"] == item["sequence"]:
                item["strength"] += 1
                boolMatch = True

        # If no match was found, append the dict object as a novel item
        if boolMatch == False:
            lstPatterns.append(dictCurrent)
        
        # Shift the moving window forward using the counter and popping the oldest object
        lstEval.append(candles[intCounter])
        lstEval.pop(0)

        # Increment the counter and reset the match boolean to False
        intCounter += 1
        boolMatch = False
    
    return lstPatterns

# Generates a list of raw patterns based on the latest symbols and volume-based candle data
def buildPatternLibrary(candles, params):

    lstPatterns = []

    # Iterate through each symbol
    for symbol in lstSymbols:

        # Generate a subset list of candles for the given symbol
        lstSubset = [x for x in lstVolume if x["symbol"] == symbol["symbol"]]

        # Execute window scoring on the subset list and return the raw patterns list
        lstPatterns = getWindowScores(lstSubset, lstPatterns, params)
    
    return lstPatterns

# Consolidates patterns into params["Pattern"]-1 sequences with buy, sell, and hold signals
def consolidatePatterns(candles, params):
    
    # Generate raw patterns list using buildPatternLibrary
    lstPatternOutput = buildPatternLibrary(candles, params)
    lstSignals = []

    # Iterate through all items in the raw patterns list
    for item in lstPatternOutput:
        
        # Initialize counter variables for signals
        intBuy = 0
        intShort = 0
        intHold = 0
        intTotal = 0

        # Further subset the raw patterns into dicts that match the sequence less the last price result
        lstMatch = [x for x in lstPatternOutput if \
            x["sequence"][:params["Pattern"]-1] == item["sequence"][:params["Pattern"]-1]]

        # Based on the items (up to 3) that match the sequence-1, increment counters by signal as well as total
        for match in lstMatch:
            if match["signal"] == "buy":
                intBuy += match["strength"]
                intTotal += match["strength"]
            
            elif match["signal"] == "short":
                intShort += match["strength"]
                intTotal += match["strength"]
            
            else:
                intHold += match["strength"]
                intTotal += match["strength"]
        
        # Append the consolidated results into a new list object with a single item per sequence-1 with signal counts
        lstSignals.append({"sequence": item["sequence"][:params["Pattern"]-1],
                            "total": intTotal,
                            "buy": intBuy,
                            "short": intShort,
                            "hold": intHold})
    
    return lstSignals


testParams = {"Pattern": 8,
                "Scoring Range": 3}

lstSignals = consolidatePatterns(lstVolume, testParams)
lstStrongSignals = [x for x in lstSignals if x["total"] > 20 and (x["short"] / x["total"] > 0.6 or x["buy"] / x["total"] > 0.6)]
csvKeys = lstStrongSignals[0].keys()

with open('patterns/pattern-8-3-20-60.csv', 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, csvKeys)
    dict_writer.writeheader()
    dict_writer.writerows(lstStrongSignals)