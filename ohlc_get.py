#!/usr/local/bin/python3
#_*_ coding: utf-8 _*_

import urllib3
import json
import datetime
import time
import sys

if len(sys.argv) > 1:
    periods = sys.argv[1]
    targetDate = ''
elif len(sys.argv) > 2:
    periods = sys.argv[1]
    targetDate = sys.argv[2]
else:
    periods = '60'
    targetDate = ''

http = urllib3.PoolManager()
url = 'https://api.cryptowat.ch/markets/bitflyer/btcfxjpy/ohlc?after=1'
resp = json.loads(http.request('GET', url).data)['result'][periods]
for r in resp:
    date = str(datetime.datetime.fromtimestamp(r[0]))
    if targetDate in date:
        print(str(datetime.datetime.fromtimestamp(r[0])) + "," + str(r[1]) + "," + str(r[2]) + "," + str(r[3]) + "," + str(r[4]) + "," + str(r[5]) + "," + str(r[6]))
