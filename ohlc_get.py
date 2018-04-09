#!/usr/local/bin/python3
#_*_ coding: utf-8 _*_

import urllib3
import json
import datetime
import time
import sys

# コマンドライン引数に日付を指定するとその日のみ抽出する(yyyy-mm-dd)
# ・例
# $python3 ohlc_get.py 2018-04-05
http = urllib3.PoolManager()
url = 'https://api.cryptowat.ch/markets/bitflyer/btcfxjpy/ohlc?after=1'
resp = json.loads(http.request('GET', url).data)['result']['60']
if len(sys.argv) > 1:
    targetDate = sys.argv[1]
else:
    targetDate = ''
for r in resp:
    date = str(datetime.datetime.fromtimestamp(r[0]))
    if targetDate in date:
        print(str(datetime.datetime.fromtimestamp(r[0])) + "," + str(r[1]) + "," + str(r[2]) + "," + str(r[3]) + "," + str(r[4]) + "," + str(r[5]) + "," + str(r[6]))
