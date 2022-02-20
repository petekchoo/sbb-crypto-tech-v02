import pandas as pd, json, requests, time
from datetime import datetime, timedelta


def get_product_candles(symbol, start, end, granularity=86400):
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


def epoch_to_isoformat(epoch):
    """
    Converts epoch date in data files to string format for API calls

    Args:
        epoch (int): seconds since epoch formatted date

    Returns:
        str: ISO 8601 formatted date string
    """
    return datetime.utcfromtimestamp(epoch).isoformat()


def update_data(granularity=86400):
    """
    For each symbol in `../data/symbols.csv`, downloads market data from Coinbase
    from the latest date in `../data/daily.csv` to current date. If the symbol does
    not exist in the daily file yet, then it will download data from Jan 1, 2017 
    to the current date. 

    TODO: Currently hard-coded to only work with daily.csv but can be extended to pull 
    additional granularities in the future.  

    Args:
        granularity (int): desired timeslice in seconds; currently only works for daily

    Returns:
        None: fills in `../data/daily.csv' with updated data
    """
    symbols = pd.read_csv('../data/symbols.csv', index_col=None)
    daily = pd.read_csv('../data/daily.csv', index_col=None)
    new_daily = pd.DataFrame() # container for all new symbol data
    for symbol in symbols['symbol']: 
        daily_symbol = daily[daily['symbol'] == symbol]
        if len(daily_symbol) > 0:   # define start 
            start = daily_symbol['time'].max()
            start = start + granularity
        else: 
            start = datetime(2017,1,1).timestamp()
        end = datetime.now()    # define end
        end = end - timedelta(hours=end.hour,        # Round now() to current day
                                minutes=end.minute,  # by removing hour, min, etc.
                                seconds=end.second,
                                microseconds=end.microsecond) 
        end = end.timestamp()
        new_data = [] # container for all api call results
        while start < end: # chunk api calls based on start and end dates
            e = start + granularity * 250 # include 250 rows in each api call
            candles = get_product_candles(symbol, 
                                        epoch_to_isoformat(start), 
                                        epoch_to_isoformat(e), 
                                        granularity=granularity)
            new_data.extend(candles)
            start = e + granularity
        new_data = pd.DataFrame(new_data, columns=['time', 'low', 'high', 'open', 'close', 'volume'])
        new_data['symbol'] = symbol # add symbol column to all responses for this symbol
        new_daily = new_daily.append(new_data)
    daily = daily.append(new_daily)
    daily.to_csv('../data/daily.csv', index=False)


# run file; can be called by live application daily
# will update the `../data/daily.csv` file if possible
update_data()