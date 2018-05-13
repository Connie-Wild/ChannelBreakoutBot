import json
import requests
import logging

class CryptoWatch:
    def getCandlestick(self, number, period):
        """
        number:ローソク足の数．period:ローソク足の期間（文字列で秒数を指定，Ex:1分足なら"60"）．cryptowatchはときどきおかしなデータ（price=0）が含まれるのでそれを除く．
        """
        #ローソク足の時間を指定
        periods = [period]
        #クエリパラメータを指定
        query = {"periods":','.join(periods)}
        #ローソク足取得
        res = json.loads(requests.get("https://api.cryptowat.ch/markets/bitflyer/btcfxjpy/ohlc", params=query).text)
        # 残りCPU時間とコストの表示
        logging.info('cost:%s remaining:%s', res["allowance"]["cost"], res["allowance"]["remaining"])
        # ローソク足のデータを入れる配列．
        data = []
        for i in periods:
            row = res["result"][i]
            length = len(row)
            for column in row[:length - (number + 1):-1]:
                # dataへローソク足データを追加．
                if column[4] != 0:
                    column = column[0:6]
                    data.append(column)
        return data[::-1]
    def getSpecifiedCandlestick(self, number, period):
        """
        number:ローソク足の数．period:ローソク足の期間（文字列で秒数を指定，Ex:1分足なら"60"）．cryptowatchはときどきおかしなデータ（price=0）が含まれるのでそれを除く
        """
        # ローソク足の時間を指定
        periods = [period]
        # クエリパラメータを指定
        query = {"periods": ','.join(periods), "after": 1}
        # ローソク足取得
        try:
            res = json.loads(requests.get("https://api.cryptowat.ch/markets/bitflyer/btcfxjpy/ohlc", params=query).text)
            # 残りCPU時間とコストの表示
            logging.info('cost:%s remaining:%s', res["allowance"]["cost"], res["allowance"]["remaining"])
            res = res["result"]
        except:
            logging.error(res)
        # ローソク足のデータを入れる配列．
        data = []
        for i in periods:
            row = res[i]
            length = len(row)
            for column in row[:length - (number + 1):-1]:
                # dataへローソク足データを追加．
                if column[4] != 0:
                    column = column[0:6]
                    data.append(column)
        return data[::-1]
