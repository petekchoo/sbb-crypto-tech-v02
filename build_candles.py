import execution, csv

lstTestBTC = execution.getMinute()
lstSymbols = execution.getSymbols()

'''
# Takes a set of candles, identifies the average volume over the past 100 days and returns that value
def averageVolume(candles):

    lstLast100 = candles[len(candles)-101:len(candles)-1]
    lstVolumes = []
    
    for candle in lstLast100:
        lstVolumes.append(float(candle["volume"]))

    return sum(lstVolumes) / len(lstVolumes)
'''

def buildVolumeCandles(candles, volume):
    
    # Initialize weighted average variables
    floatRunningAmount = 0.00
    floatRunningVolume = 0.00

    # Initialize empty list of volume-based candles to be returned by the function
    lstVolumeCandles = []
    
    # Initialize dictionary objects for parsing and accumulating
    dictParsedCandle = {}
    dictCurrentCandle = {}
    dictPartialCandle = {}

    for candle in candles:

        dictParsedCandle = candle

        # If current candle is empty, check for a partial candle
        if len(dictCurrentCandle) == 0:
            
            # If the partial candle is also empty, initialize the current candle with the parsed candle
            if len(dictPartialCandle) == 0:
            
                dictCurrentCandle = dictParsedCandle
                floatRunningAmount += float(dictParsedCandle["volume"]) * float(dictParsedCandle["close"])
                floatRunningVolume += float(dictParsedCandle["volume"])
            
            # If the partial candle isn't empty, initialize the current candle with the partial candle
            # and add the values from the parsed candle, checking highs and lows as you go
            else:

                dictCurrentCandle = dictPartialCandle
                floatRunningAmount += float(dictPartialCandle["volume"]) * float(dictPartialCandle["close"])
                floatRunningVolume += float(dictPartialCandle["volume"])

                floatRunningAmount += float(dictParsedCandle["volume"]) * float(dictParsedCandle["close"])
                floatRunningVolume += float(dictParsedCandle["volume"])

                if float(dictParsedCandle["high"]) > float(dictCurrentCandle["high"]):
                    dictCurrentCandle["high"] = dictParsedCandle["high"]
        
                elif float(dictParsedCandle["low"]) < float(dictCurrentCandle["low"]):
                    dictCurrentCandle["low"] = dictParsedCandle["low"]

        # Else if the currently accumulated volume is less than the volume limit...
        elif floatRunningVolume < volume:

            # Check if the volume of the parsed candle will meet or exceed the volume limit (split case)
            # Note: in the unlikely event the parsed candle volume EXACTLY meets the volume limit,
            # a partial candle will be initialized with zero volume, which has no impact on the
            # weighted price calculation for the next volume candle
            if floatRunningVolume + float(dictParsedCandle["volume"]) >= volume:

                # Set the partial candle to the parsed candle and update its volume to the remainder volume
                dictPartialCandle = dictParsedCandle
                dictPartialCandle["volume"] = float(dictParsedCandle["volume"]) - (volume - floatRunningVolume)
                
                # "Top off" weighted average variables with the volume needed to achieve the volume limit
                floatRunningAmount += (volume - floatRunningVolume) * float(dictParsedCandle["close"])
                floatRunningVolume = volume

                # Update current candle with the final volume and set the close price to the
                # weighted average price, check if high / low needs to be updated, then add
                # the current candle to the list of volume candles
                dictCurrentCandle["volume"] = volume
                dictCurrentCandle["close"] = floatRunningAmount / floatRunningVolume
                
                if float(dictParsedCandle["high"]) > float(dictCurrentCandle["high"]):
                    dictCurrentCandle["high"] = dictParsedCandle["high"]
        
                elif float(dictParsedCandle["low"]) < float(dictCurrentCandle["low"]):
                    dictCurrentCandle["low"] = dictParsedCandle["low"]
                
                lstVolumeCandles.append(dictCurrentCandle)
                
                # Reinitialize current candle and weighted average variables
                dictCurrentCandle = {}
                floatRunningAmount = 0.00
                floatRunningVolume = 0.00

            # If the volume of the parsed candle won't exceed the volume limit, just increment, check
            # the highs and lows, and keep going
            else:
                floatRunningAmount += float(dictParsedCandle["volume"]) * float(dictParsedCandle["close"])
                floatRunningVolume += float(dictParsedCandle["volume"])

                if float(dictParsedCandle["high"]) > float(dictCurrentCandle["high"]):
                    dictCurrentCandle["high"] = dictParsedCandle["high"]
        
                elif float(dictParsedCandle["low"]) < float(dictCurrentCandle["low"]):
                    dictCurrentCandle["low"] = dictParsedCandle["low"]
                
    return lstVolumeCandles

print(buildVolumeCandles(lstTestBTC, 100.00))