import pandas as pd, json, requests, time
from datetime import datetime, timedelta


def getProductCandles(symbol, start, end, granularity=86400):
    """
    Formats API call to Coinbase to download historical candlestick data for `symbol`
    Reference: https://docs.cloud.coinbase.com/exchange/reference/exchangerestapi_getproductcandles

    Args:
        symbol (str): ticker symbol to download
        start (str): strt time in ISO 8601
        end (str): end time in ISO 8601
        granularity (int): desired timeslice in seconds

    Returns:
        list: list of dicts, which represent individual candles
    """
    url = 'https://api.exchange.coinbase.com/products/' + symbol +'/candles/'
    params = {
        'start': start,
        'end': end,
        'granularity': granularity
    }
    headers = {'Accept': 'application/json'}
    time.sleep(0.15) # Rate limit is 10 requests per second
    response = requests.request('GET', url, headers=headers, params=params)
    lst = json.loads(response.text)
    return lst


def epochToISOFormat(epoch):
    """
    Converts epoch date in data files to string format for API calls

    Args:
        epoch (int): seconds since epoch formatted date

    Returns:
        str: ISO 8601 formatted date string
    """
    return datetime.utcfromtimestamp(epoch).isoformat()


def updateData(granularity=86400):
    """
    For each symbol in `data/symbols.csv`, downloads market data from Coinbase
    from the latest date in `data/daily.csv` to current date. If the symbol does
    not exist in the daily file yet, then it will download data from Jan 1, 2017 
    to the current date. 

    Args:
        granularity (int): desired timeslice in seconds; currently only works for daily

    Returns:
        None: fills in `data/daily.csv' with updated data
    """
    if granularity == 86400: 
        fileName = 'daily.csv'
    elif granularity == 60: 
        fileName = 'minute.csv'
    else: 
        print('updateData error: choose valid granularity')
        return None

    symbols = pd.read_csv('data/symbols.csv', index_col=None)
    file = pd.read_csv('data/' + fileName, index_col=None)
    newFile = pd.DataFrame() # container for all new symbol data
    for symbol in symbols['symbol']: 
        print('Fetching ', symbol, '...')
        fileSymbol = file[file['symbol'] == symbol]
        if len(fileSymbol) > 0:   # define start 
            start = fileSymbol['time'].max()
            start = start + granularity
        else: 
            start = datetime(2017,1,1).timestamp()
        end = datetime.now()    # define end
        # end = end - timedelta(hours=end.hour,        # Round now() to current day
        #                         minutes=end.minute,  # by removing hour, min, etc.
        #                         seconds=end.second,
        #                         microseconds=end.microsecond) 
        end = end.timestamp()
        newData = [] # container for all api call results
        while start < end: # chunk api calls based on start and end dates
            e = start + granularity * 250 # include 250 rows in each api call
            candles = getProductCandles(symbol, 
                                        epochToISOFormat(start), 
                                        epochToISOFormat(e), 
                                        granularity=granularity)
            newData.extend(candles)
            start = e + granularity
        newData = pd.DataFrame(newData, columns=['time', 'low', 'high', 'open', 'close', 'volume'])
        newData['symbol'] = symbol # add symbol column to all responses for this symbol
        newFile = newFile.append(newData)
    file = file.append(newFile)
    file = file.sort_values(['symbol', 'time']) # inefficient, but it will re-sort the file
    file.to_csv('data/' + fileName, index=False)


# run file; can be called by live application daily
# will update the data file if possible
updateData()