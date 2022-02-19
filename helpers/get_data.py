# get_data.py: script to pull a bunch of data and create datafiles, can be run daily
#             # get_product_candles(ticker, start, end, granularity) --> data/<ticker>.csv
#                 # if data file does not already exist, get a bunch of historical data
#                 # if data file does exist, get current date of data and update data file