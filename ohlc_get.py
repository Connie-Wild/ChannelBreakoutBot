import urllib3
import json
import datetime
import time

http = urllib3.PoolManager()
url = 'https://api.cryptowat.ch/markets/bitflyer/btcfxjpy/ohlc?after=1' 
resp = json.loads(http.request('GET', url).data)['result']['60']
for r in resp:
    print(str(datetime.datetime.fromtimestamp(r[0])) + "," + str(r[1]) + "," + str(r[2]) + "," + str(r[3]) + "," + str(r[4]) + "," + str(r[5]) + "," + str(r[6]))
