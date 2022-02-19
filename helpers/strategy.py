# strategy.py: takes in parameters for a trading day (i.e. account, current date signals)
#                     and executes trade decision
#             # trading_day() --> 

# Read relevant csv files into dictionaries

import csv
import datetime

dictSample = csv.DictReader(open('data/sample.csv', mode='r', encoding='utf-8-sig'))
# dict200 = 

for item in dictSample:
    print(datetime.datetime.fromtimestamp(int(item["time"])))
    print("high:", item["high"])
    print("low:", item["low"])
