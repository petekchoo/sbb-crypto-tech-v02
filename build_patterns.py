from tkinter import N
import execution, indicators, csv, datetime

# Building a function (TBD module) to build out and store trading patterns.

lstSymbols = execution.getSymbols()
lstVolume = execution.getVolume()

def buildPatternLibrary(candles, params):

    lstPatterns = []

    for symbol in lstSymbols:

        lstSubset = [x for x in lstVolume if x["symbol"] == symbol["symbol"]]
        lstPatterns = execution.getWindowScores(lstSubset, lstPatterns, params)
    
    return lstPatterns

def consolidatePatterns(candles, params):
    lstPatternOutput = buildPatternLibrary(lstVolume, testParams)
    lstSignals = []

    for item in lstPatternOutput:

        lstMatch = [x for x in lstPatternOutput if \
            x["sequence"][:testParams["Pattern"]-1] == item["sequence"][:testParams["Pattern"]-1]]
        
        intBuy = 0
        intShort = 0
        intHold = 0
        intTotal = 0

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
        
        lstSignals.append({"sequence": item["sequence"][:testParams["Pattern"]-1],
                            "total": intTotal,
                            "buy": intBuy,
                            "short": intShort,
                            "hold": intHold})
    
    return lstSignals