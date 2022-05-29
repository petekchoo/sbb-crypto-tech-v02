import execution, csv

lstTestBTC = execution.getMinute()
lstSymbols = execution.getSymbols()

# Takes a set of candles and a window parameter to determine the volume limit to be used when
# rebuilding volume-based candles
def setVolumeLimit(candles, params):
    """
    Args:
        candles (list of dicts): set of candles to be evaluated
        param (dict): contains two value/key pairs:
            window (str): date-level of the window, either hourly, daily, weekly, or monthly
            range (int): how many hours / days / weeks / months to be used to calc the average

    Returns:
        floatVolumeLimit (float): the average of the last X candles as determined by param
    
    Reference:
        hour == 60 candles
        day == 1440 candles
        week == 10080 candles
        month == 43800 (average)
    """

    # Initialize total volume variable
    floatVolumeSum = 0.00

    # Convert window parameter (str) into corresponding # of candles, set to variable:
    intWindow = 0
    
    if params["window"] == "hour":
        intWindow = 60
    
    elif params["window"] == "day":
        intWindow = 1440
    
    elif params["window"] == "week":
        intWindow = 10080

    elif params["window"] == "month":
        intWindow = 43800

    # First check if there are enough candles based on the params
    if len(candles) < (intWindow * params["range"]):
        print("Not enough candles!")
        return 0
    
    else: ### NOTE: something stupid here. May be easier to just sum all volume from the subset
        # of the list then divide everything by # of days?
        
       lstSubset = candles[len(candles)-(intWindow * params["range"]):]
       floatVolumeSum = sum(float(item["volume"]) for item in lstSubset)
    
    # Return the average volume (total volume accumulated divided by # of hours / days / etc. parsed)
    return floatVolumeSum / params["range"]

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
            
                dictCurrentCandle = dictParsedCandle.copy()
                floatRunningAmount += float(dictParsedCandle["volume"]) * float(dictParsedCandle["close"])
                floatRunningVolume += float(dictParsedCandle["volume"])
            
            # If the partial candle isn't empty, initialize the current candle with the partial candle
            # and add the values from the parsed candle, checking highs and lows as you go
            else:

                dictCurrentCandle = dictPartialCandle.copy()
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
                dictPartialCandle = dictParsedCandle.copy()
                dictPartialCandle["volume"] = float(dictParsedCandle["volume"]) - (volume - floatRunningVolume)
                
                # "Top off" weighted average variables with the volume needed to achieve the volume limit
                floatRunningAmount += (volume - floatRunningVolume) * float(dictParsedCandle["close"])
                floatRunningVolume = volume

                # Update current candle with the final volume and set the close price to the
                # weighted average price, set the date to the date of the parsed candle, 
                # check if high / low needs to be updated, then add the current candle to the
                # list of volume candles
                dictCurrentCandle["volume"] = volume
                dictCurrentCandle["close"] = floatRunningAmount / floatRunningVolume
                dictCurrentCandle["time"] = dictParsedCandle["time"]
                
                if float(dictParsedCandle["high"]) > float(dictCurrentCandle["high"]):
                    dictCurrentCandle["high"] = dictParsedCandle["high"]
        
                elif float(dictParsedCandle["low"]) < float(dictCurrentCandle["low"]):
                    dictCurrentCandle["low"] = dictParsedCandle["low"]
                
                lstVolumeCandles.append(dictCurrentCandle)
                
                # Reinitialize current candle and weighted average variables
                dictCurrentCandle = {}
                floatRunningAmount = 0.00
                floatRunningVolume = 0.00

            # If the volume of the parsed candle won't exceed the volume limit, just increment the running
            # values, check the highs and lows, and keep going
            else:
                floatRunningAmount += float(dictParsedCandle["volume"]) * float(dictParsedCandle["close"])
                floatRunningVolume += float(dictParsedCandle["volume"])

                if float(dictParsedCandle["high"]) > float(dictCurrentCandle["high"]):
                    dictCurrentCandle["high"] = dictParsedCandle["high"]
        
                elif float(dictParsedCandle["low"]) < float(dictCurrentCandle["low"]):
                    dictCurrentCandle["low"] = dictParsedCandle["low"]
                
    return lstVolumeCandles

print(setVolumeLimit(lstTestBTC, {"window": "hour", "range": 24}))

''' Csv write code
dictVolumeCandles = buildVolumeCandles(lstTestBTC, 10000.00)
csvKeys = dictVolumeCandles[0].keys()

with open('data/volume.csv', 'a', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, csvKeys)
    # dict_writer.writeheader()
    dict_writer.writerows(dictVolumeCandles)
'''