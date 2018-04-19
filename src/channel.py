#_*_ coding: utf-8 _*_
#https://sshuhei.com

import json
import requests
import csv
import math
import pandas as pd
import time
import datetime
import logging
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub_tornado import PubNubTornado
from pubnub.pnconfiguration import PNReconnectionPolicy
from tornado import gen
import threading
from collections import deque
from . import bforder
from . import cryptowatch

class ChannelBreakOut:
    def __init__(self):
        #config.jsonの読み込み
        f = open('config.json', 'r', encoding="utf-8")
        config = json.load(f)
        self.cryptowatch = cryptowatch.CryptoWatch()
        #pubnubから取得した約定履歴を保存するリスト（基本的に不要．）
        self._executions = deque(maxlen=300)
        self._lot = 0.01
        self._product_code = config["product_code"]
        #各パラメタ．
        self._entryTerm = 10
        self._closeTerm = 5
        self._rangeTerm = 15
        self._rangeTh = 5000
        self._waitTerm = 5
        self._waitTh = 20000
        self.rangePercent = None
        self.rangePercentTerm = None
        self._candleTerm = "1T"
        #現在のポジション．1ならロング．-1ならショート．0ならポジションなし．
        self._pos = 0
        #注文執行コスト．遅延などでこの値幅を最初から取られていると仮定する
        self._cost = 3000
        self.order = bforder.BFOrder()
        #取引所のヘルスチェック
        self.healthCheck = config["healthCheck"]
        #ラインに稼働状況を通知
        self.line_notify_token = config["line_notify_token"]
        self.line_notify_api = 'https://notify-api.line.me/api/notify'
        # グラフ表示
        self.showFigure = False
        # バックテスト結果のグラフをLineで送る
        self.sendFigure = False
        # バックテストのトレード詳細をログ出力する
        self.showTradeDetail = False
        # optimization用のOHLCcsvファイル
        self.fileName = None

    @property
    def cost(self):
        return self._cost

    @cost.setter
    def cost(self, value):
        self._cost = value

    @property
    def candleTerm(self):
        return self._candleTerm
    @candleTerm.setter
    def candleTerm(self, val):
        """
        valは"5T"，"1H"などのString
        """
        self._candleTerm = val

    @property
    def waitTh(self):
        return self._waitTh
    @waitTh.setter
    def waitTh(self, val):
        self._waitTh = val

    @property
    def waitTerm(self):
        return self._waitTerm
    @waitTerm.setter
    def waitTerm(self, val):
        self._waitTerm = val

    @property
    def rangeTh(self):
        return self._rangeTh
    @rangeTh.setter
    def rangeTh(self,val):
        self._rangeTh = val

    @property
    def rangeTerm(self):
        return self._rangeTerm
    @rangeTerm.setter
    def rangeTerm(self,val):
        self._rangeTerm = val

    @property
    def executions(self):
        return self._executions
    @executions.setter
    def executions(self, val):
        self._executions = val

    @property
    def pos(self):
        return self._pos
    @pos.setter
    def pos(self, val):
        self._pos = int(val)

    @property
    def lot(self):
        return self._lot
    @lot.setter
    def lot(self, val):
        self._lot = round(val,3)

    @property
    def product_code(self):
        return self._product_code
    @product_code.setter
    def product_code(self, val):
        self._product_code = val

    @property
    def entryTerm(self):
        return self._entryTerm
    @entryTerm.setter
    def entryTerm(self, val):
        self._entryTerm = int(val)

    @property
    def closeTerm(self):
        return self._closeTerm
    @closeTerm.setter
    def closeTerm(self, val):
        self._closeTerm = int(val)

    def calculateLot(self, margin):
        """
        証拠金からロットを計算する関数．
        """
        lot = math.floor(margin*10**(-4))*10**(-2)
        return round(lot,2)

    def calculateLines(self, df_candleStick, term, rangePercent, rangePercentTerm):
        """
        期間高値・安値を計算する．
        candleStickはcryptowatchのローソク足．termは安値，高値を計算する期間．（5ならローソク足5本文の安値，高値．)
        """
        lowLine = []
        highLine = []
        if rangePercent == None or rangePercentTerm == None:
            for i in range(len(df_candleStick.index)):
                if i < term:
                    lowLine.append(df_candleStick["low"][i])
                    highLine.append(df_candleStick["high"][i])
                else:
                    low = min([price for price in df_candleStick["low"][i-term:i-1]])
                    high = max([price for price in df_candleStick["high"][i-term:i-1]])
                    lowLine.append(low)
                    highLine.append(high)
        else:
            priceRange = self.calculatePriceRange(df_candleStick, 1)
            for i in range(len(df_candleStick.index)):
                if i < term:
                    lowLine.append(df_candleStick["low"][i] - priceRange[i] * rangePercent)
                    highLine.append(df_candleStick["high"][i] + priceRange[i] * rangePercent)
                elif i < rangePercentTerm:
                    priceRangeMean = sum(priceRange[i-term:i-1]) / term
                    low = min([price for price in df_candleStick["low"][i-term:i-1]]) - priceRangeMean * rangePercent
                    high = max([price for price in df_candleStick["high"][i-term:i-1]]) + priceRangeMean * rangePercent
                    lowLine.append(low)
                    highLine.append(high)
                else:
                    priceRangeMean = sum(priceRange[i-rangePercentTerm:i-1]) / rangePercentTerm
                    low = min([price for price in df_candleStick["low"][i-term:i-1]]) - priceRangeMean * rangePercent
                    high = max([price for price in df_candleStick["high"][i-term:i-1]]) + priceRangeMean * rangePercent
                    lowLine.append(low)
                    highLine.append(high)
        return (lowLine, highLine)

    def calculatePriceRange(self, df_candleStick, term):
        """
        termの期間の値幅を計算．
        """
        if term == 1:
            #low = [min([df_candleStick["close"][i].min(), df_candleStick["open"][i].min()]) for i in range(len(df_candleStick.index))]
            #high = [max([df_candleStick["close"][i].max(), df_candleStick["open"][i].max()]) for i in range(len(df_candleStick.index))]
            low = [df_candleStick["low"][i] for i in range(len(df_candleStick.index))]
            high = [df_candleStick["high"][i] for i in range(len(df_candleStick.index))]
            low = pd.Series(low)
            high = pd.Series(high)
            priceRange = [high.iloc[i]-low.iloc[i] for i in range(len(df_candleStick.index))]
        else:
            #low = [min([df_candleStick["close"][i-term+1:i].min(), df_candleStick["open"][i-term+1:i].min()]) for i in range(len(df_candleStick.index))]
            #high = [max([df_candleStick["close"][i-term+1:i].max(), df_candleStick["open"][i-term+1:i].max()]) for i in range(len(df_candleStick.index))]
            low = [df_candleStick["low"][i-term+1:i].min() for i in range(len(df_candleStick.index))]
            high = [df_candleStick["high"][i-term+1:i].max() for i in range(len(df_candleStick.index))]
            low = pd.Series(low)
            high = pd.Series(high)
            priceRange = [high.iloc[i]-low.iloc[i] for i in range(len(df_candleStick.index))]
        return priceRange

    def isRange(self, df_candleStick, term, th):
        """
        レンジ相場かどうかをTrue,Falseの配列で返す．termは期間高値・安値の計算期間．thはレンジ判定閾値．
        """
        #値幅での判定．
        if th != None:
            priceRange = self.calculatePriceRange(df_candleStick, term)
            isRange = [th > i for i in priceRange]
        #終値の標準偏差の差分が正か負かでの判定．
        elif th == None and term != None:
            df_candleStick["std"] = [df_candleStick["close"][i-term+1:i].std() for i in range(len(df_candleStick.index))]
            df_candleStick["std_slope"] = [df_candleStick["std"][i]-df_candleStick["std"][i-1] for i in range(len(df_candleStick.index))]
            isRange = [i > 0 for i in df_candleStick["std_slope"]]
        else:
            isRange = [False for i in df_candleStick.index]
        return isRange

    def judge(self, df_candleStick, entryHighLine, entryLowLine, closeHighLine, closeLowLine, entryTerm):
        """
        売り買い判断．ローソク足の高値が期間高値を上抜けたら買いエントリー．（2）ローソク足の安値が期間安値を下抜けたら売りエントリー．judgementリストは[買いエントリー，売りエントリー，買いクローズ（売り），売りクローズ（買い）]のリストになっている．（二次元リスト）リスト内リストはの要素は，0（シグナルなし）,価格（シグナル点灯）を取る．
        """
        judgement = [[0,0,0,0] for i in range(len(df_candleStick.index))]
        for i in range(len(df_candleStick.index)):
            #上抜けでエントリー
            if df_candleStick["high"][i] > entryHighLine[i] and i >= entryTerm:
                judgement[i][0] = round((df_candleStick["high"][i] + entryHighLine[i]*2) / 3)
            #下抜けでエントリー
            if df_candleStick["low"][i] < entryLowLine[i] and i >= entryTerm:
                judgement[i][1] = round((df_candleStick["low"][i] + entryLowLine[i]*2) / 3)
            #下抜けでクローズ
            if df_candleStick["low"][i] < closeLowLine[i] and i >= entryTerm:
                judgement[i][2] = round((df_candleStick["low"][i] + closeLowLine[i]*2) / 3)
            #上抜けでクローズ
            if df_candleStick["high"][i] > closeHighLine[i] and i >= entryTerm:
                judgement[i][3] = round((df_candleStick["high"][i] + closeHighLine[i]*2) / 3)
            else:
                pass
        return judgement

    def judgeForLoop(self, high, low, entryHighLine, entryLowLine, closeHighLine, closeLowLine):
        """
        売り買い判断．入力した価格が期間高値より高ければ買いエントリー，期間安値を下抜けたら売りエントリー．judgementリストは[買いエントリー，売りエントリー，買いクローズ（売り），売りクローズ（買い）]のリストになっている．（値は0or1）
        ローソク足は1分ごとに取得するのでインデックスが-1のもの（現在より1本前）をつかう．
        """
        judgement = [0,0,0,0]
        #上抜けでエントリー
        if high > entryHighLine[-1]:
            judgement[0] = 1
        #下抜けでエントリー
        if low < entryLowLine[-1]:
            judgement[1] = 1
        #下抜けでクローズ
        if low < closeLowLine[-1]:
            judgement[2] = 1
        #上抜けでクローズ
        if high > closeHighLine[-1]:
            judgement[3] = 1
        return judgement

    #エントリーラインおよびクローズラインで約定すると仮定する．
    def backtest(self, judgement, df_candleStick, lot, rangeTh, rangeTerm, originalWaitTerm=10, waitTh=10000, cost = 0):
        #エントリーポイント，クローズポイントを入れるリスト
        buyEntrySignals = []
        sellEntrySignals = []
        buyCloseSignals = []
        sellCloseSignals = []
        nOfTrade = 0
        pos = 0
        pl = []
        pl.append(0)
        #トレードごとの損益
        plPerTrade = []
        #取引時の価格を入れる配列．この価格でバックテストのplを計算する．（ので，どの価格で約定するかはテストのパフォーマンスに大きく影響を与える．）
        buy_entry = []
        buy_close = []
        sell_entry = []
        sell_close = []
        #各ローソク足について，レンジ相場かどうかの判定が入っている配列
        isRange =  self.isRange(df_candleStick, rangeTerm, rangeTh)
        #基本ロット．勝ちトレードの直後はロットを落とす．
        originalLot = lot
        #勝ちトレード後，何回のトレードでロットを落とすか．
        waitTerm = 0
        # 取引履歴 [time, order, price, profit]
        trade_log = []
        for i in range(len(judgement)):
            if i > 0:
                lastPL = pl[-1]
                pl.append(lastPL)
            #エントリーロジック
            if pos == 0 and not isRange[i]:
                #ロングエントリー
                if judgement[i][0] != 0:
                    pos += 1
                    buy_entry.append(judgement[i][0])
                    buyEntrySignals.append(df_candleStick.index[i])
                    trade_log.append([df_candleStick.index[i], 'buy  entry', judgement[i][0]])
                #ショートエントリー
                elif judgement[i][1] != 0:
                    pos -= 1
                    sell_entry.append(judgement[i][1])
                    sellEntrySignals.append(df_candleStick.index[i])
                    trade_log.append([df_candleStick.index[i], 'sell entry', judgement[i][1]])
            #ロングクローズロジック
            elif pos == 1:
                #ロングクローズ
                if judgement[i][2] != 0:
                    nOfTrade += 1
                    pos -= 1
                    buy_close.append(judgement[i][2])
                    #値幅
                    plRange = buy_close[-1] - buy_entry[-1]
                    pl[-1] = pl[-2] + (plRange-self.cost) * lot
                    buyCloseSignals.append(df_candleStick.index[i])
                    plPerTrade.append((plRange-self.cost)*lot)
                    trade_log.append([df_candleStick.index[i], 'buy  close', judgement[i][2], (plRange-self.cost)*lot])
                    #waitTh円以上の値幅を取った場合，次の10トレードはロットを1/10に落とす．
                    if plRange > waitTh:
                        waitTerm = originalWaitTerm
                        lot = originalLot/10
                    elif waitTerm > 0:
                        waitTerm -= 1
                        lot = originalLot/10
                    if waitTerm == 0:
                         lot = originalLot
            #ショートクローズロジック
            elif pos == -1:
                #ショートクローズ
                if judgement[i][3] != 0:
                    nOfTrade += 1
                    pos += 1
                    sell_close.append(judgement[i][3])
                    plRange = sell_entry[-1] - sell_close[-1]
                    pl[-1] = pl[-2] + (plRange-self.cost) * lot
                    sellCloseSignals.append(df_candleStick.index[i])
                    plPerTrade.append((plRange-self.cost)*lot)
                    trade_log.append([df_candleStick.index[i], 'sell close', judgement[i][3], (plRange-self.cost)*lot])
                    #waitTh円以上の値幅を取った場合，次の10トレードはロットを1/10に落とす．
                    if plRange > waitTh:
                        waitTerm = originalWaitTerm
                        lot = originalLot/10
                    elif waitTerm > 0:
                        waitTerm -= 1
                        lot = originalLot/10
                    if waitTerm == 0:
                         lot = originalLot

            #さらに，クローズしたと同時にエントリーシグナルが出ていた場合のロジック．
            if pos == 0 and not isRange[i]:
                #ロングエントリー
                if judgement[i][0] != 0:
                    pos += 1
                    buy_entry.append(judgement[i][0])
                    buyEntrySignals.append(df_candleStick.index[i])
                    trade_log.append([df_candleStick.index[i], 'buy  entry', judgement[i][0]])
                #ショートエントリー
                elif judgement[i][1] != 0:
                    pos -= 1
                    sell_entry.append(judgement[i][1])
                    sellEntrySignals.append(df_candleStick.index[i])
                    trade_log.append([df_candleStick.index[i], 'sell entry', judgement[i][1]])

        #最後にポジションを持っていたら，期間最後のローソク足の終値で反対売買．
        if pos == 1:
            buy_close.append(df_candleStick["close"][-1])
            plRange = buy_close[-1] - buy_entry[-1]
            pl[-1] = pl[-2] + plRange * lot
            pos -= 1
            buyCloseSignals.append(df_candleStick.index[-1])
            nOfTrade += 1
            plPerTrade.append(plRange*lot)
            trade_log.append([df_candleStick.index[-1], 'buy  close', df_candleStick["close"][-1], plRange*lot])
        elif pos ==-1:
            sell_close.append(df_candleStick["close"][-1])
            plRange = sell_entry[-1] - sell_close[-1]
            pl[-1] = pl[-2] + plRange * lot
            pos +=1
            sellCloseSignals.append(df_candleStick.index[-1])
            nOfTrade += 1
            plPerTrade.append(plRange*lot)
            trade_log.append([df_candleStick.index[-1], 'sell close', df_candleStick["close"][-1], plRange*lot])
        return (pl, buyEntrySignals, sellEntrySignals, buyCloseSignals, sellCloseSignals, nOfTrade, plPerTrade, trade_log)

    def describeResult(self):
        """
        signalsは買い，売り，中立が入った配列
        """
        if self.fileName == None:
            if "H" in self.candleTerm:
                candleStick = self.cryptowatch.getSpecifiedCandlestick(2000, "3600")
            else:
                candleStick = self.cryptowatch.getSpecifiedCandlestick(5999, "60")
        else:
            candleStick = self.readDataFromFile(self.fileName)

        if self.candleTerm != None:
            df_candleStick = self.processCandleStick(candleStick, self.candleTerm)
        else:
            df_candleStick = self.fromListToDF(candleStick)

        entryLowLine, entryHighLine = self.calculateLines(df_candleStick, self.entryTerm, self.rangePercent, self.rangePercentTerm)
        closeLowLine, closeHighLine = self.calculateLines(df_candleStick, self.closeTerm, self.rangePercent, self.rangePercentTerm)
        judgement = self.judge(df_candleStick, entryHighLine, entryLowLine, closeHighLine, closeLowLine, self.entryTerm)
        pl, buyEntrySignals, sellEntrySignals, buyCloseSignals, sellCloseSignals, nOfTrade, plPerTrade, tradeLog = self.backtest(judgement, df_candleStick, 1, self.rangeTh, self.rangeTerm, originalWaitTerm=self.waitTerm, waitTh=self.waitTh, cost=self.cost)

        if self.showFigure:
            from src import candle_plot
            candle_plot.show(df_candleStick, pl, buyEntrySignals, sellEntrySignals, buyCloseSignals, sellCloseSignals)
        elif self.sendFigure:
            from src import candle_plot
            # save as png
            today = datetime.datetime.now().strftime('%Y%m%d')
            number = "_" + str(len(pl))
            fileName = "png/" + today + number + ".png"
            candle_plot.save(df_candleStick, pl, buyEntrySignals, sellEntrySignals, buyCloseSignals, sellCloseSignals, fileName)
            self.lineNotify("Result of backtest",fileName)
        else:
            pass

        #各統計量の計算および表示．
        winTrade = sum([1 for i in plPerTrade if i > 0])
        loseTrade = sum([1 for i in plPerTrade if i < 0])
        try:
            winPer = round(winTrade/(winTrade+loseTrade) * 100,2)
        except:
            winPer = 100

        winTotal = sum([i for i in plPerTrade if i > 0])
        loseTotal = sum([i for i in plPerTrade if i < 0])
        try:
            profitFactor = round(winTotal/-loseTotal, 3)
        except:
            profitFactor = float("inf")

        maxProfit = max(plPerTrade, default=0)
        maxLoss = min(plPerTrade, default=0)

        logging.info('showFigure :%s, sendFigure :%s',self.showFigure, self.sendFigure)
        logging.info('Period: %s > %s', df_candleStick.index[0], df_candleStick.index[-1])
        logging.info("Total pl: {}JPY".format(int(pl[-1])))
        logging.info("The number of Trades: {}".format(nOfTrade))
        logging.info("The Winning percentage: {}%".format(winPer))
        logging.info("The profitFactor: {}".format(profitFactor))
        logging.info("The maximum Profit and Loss: {}JPY, {}JPY".format(maxProfit, maxLoss))
        if self.showTradeDetail:
            logging.info("==Trade detail==")
            for log in tradeLog:
                profit = log[3] if len(log) > 3 else ''
                logging.info("%s %s %s %s", log[0], log[1], log[2], profit)
            logging.info("============")

        return pl[-1], profitFactor, maxLoss, winPer

    def fromListToDF(self, candleStick):
        """
        Listのローソク足をpandasデータフレームへ．
        """
        date = [price[0] for price in candleStick]
        priceOpen = [int(price[1]) for price in candleStick]
        priceHigh = [int(price[2]) for price in candleStick]
        priceLow = [int(price[3]) for price in candleStick]
        priceClose = [int(price[4]) for price in candleStick]
        volume = [int(price[5]) for price in candleStick]
        date_datetime = map(datetime.datetime.fromtimestamp, date)
        dti = pd.DatetimeIndex(date_datetime)
        df_candleStick = pd.DataFrame({"open" : priceOpen, "high" : priceHigh, "low": priceLow, "close" : priceClose, "volume" : volume}, index=dti)
        return df_candleStick

    def processCandleStick(self, candleStick, timeScale):
        """
        1分足データから各時間軸のデータを作成.timeScaleには5T（5分），H（1時間）などの文字列を入れる
        """
        df_candleStick = self.fromListToDF(candleStick)
        processed_candleStick = df_candleStick.resample(timeScale).agg({'open': 'first','high': 'max','low': 'min','close': 'last',"volume" : "sum"})
        processed_candleStick = processed_candleStick.dropna()
        return processed_candleStick

    #csvファイル（ヘッダなし）からohlcデータを作成．
    def readDataFromFile(self, filename):
        for i in range(1, 10, 1):
            with open(filename, 'r', encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader)
                for row in reader:
                    candleStick = [row for row in reader if row[4] != "0"]
        dtDate = [datetime.datetime.strptime(data[0], '%Y-%m-%d %H:%M:%S') for data in candleStick]
        dtTimeStamp = [dt.timestamp() for dt in dtDate]
        for i in range(len(candleStick)):
            candleStick[i][0] = dtTimeStamp[i]
        candleStick = [[float(i) for i in data] for data in candleStick]
        return candleStick

    def lineNotify(self, message, fileName=None):
        payload = {'message': message}
        headers = {'Authorization': 'Bearer ' + self.line_notify_token}
        if fileName == None:
            try:
                requests.post(self.line_notify_api, data=payload, headers=headers)
            except:
                pass
        else:
            try:
                files = {"imageFile": open(fileName, "rb")}
                requests.post(self.line_notify_api, data=payload, headers=headers, files = files)
            except:
                pass

    def describePLForNotification(self, pl, df_candleStick):
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            close = df_candleStick["close"]
            index = range(len(pl))
            # figure
            fig = plt.figure(figsize=(20,12))
            #for price
            ax = fig.add_subplot(2, 1, 1)
            ax.plot(df_candleStick.index, close)
            ax.set_xlabel('Time')
            # y axis
            ax.set_ylabel('The price[JPY]')
            #for PLcurve
            ax = fig.add_subplot(2, 1, 2)
            # plot
            ax.plot(index, pl, color='b', label='The PL curve')
            ax.plot(index, [0]*len(pl), color='b',)
            # x axis
            ax.set_xlabel('The number of Trade')
            # y axis
            ax.set_ylabel('The estimated Profit/Loss(JPY)')
            # legend and title
            ax.legend(loc='best')
            ax.set_title('The PL curve(Time span:{})'.format(self.candleTerm))
            # save as png
            today = datetime.datetime.now().strftime('%Y%m%d')
            number = "_" + str(len(pl))
            fileName = "png/" + today + number + ".png"
            plt.savefig(fileName)
            plt.close()
        except:
            fileName = ""
        return fileName

    def loop(self):
        """
        注文の実行ループを回す関数
        """
        self.executionsProcess()
        #pubnubが回り始めるまで待つ．
        time.sleep(20)
        pos = 0
        pl = []
        pl.append(0)
        lastPositionPrice = 0
        lot = self.lot
        originalLot = self.lot
        waitTerm = 0

        # 証拠金の状態を取得
        collateral = self.order.getcollateral()
        logging.info('collateral:%s', collateral["collateral"])

        try:
            if "H" in self.candleTerm:
                candleStick = self.cryptowatch.getCandlestick(480, "3600")
            else:
                candleStick = self.cryptowatch.getCandlestick(480, "60")
        except:
            logging.error("Unknown error happend when you requested candleStick")

        if self.candleTerm == None:
            df_candleStick = self.fromListToDF(candleStick)
        else:
            df_candleStick = self.processCandleStick(candleStick, self.candleTerm)

        entryLowLine, entryHighLine = self.calculateLines(df_candleStick, self.entryTerm, self.rangePercent, self.rangePercentTerm)
        closeLowLine, closeHighLine = self.calculateLines(df_candleStick, self.closeTerm, self.rangePercent, self.rangePercentTerm)

        #直近約定件数30件の高値と安値
        high = max([self.executions[-1-i]["price"] for i in range(30)])
        low = min([self.executions[-1-i]["price"] for i in range(30)])

        message = "Starting for channelbreak."
        logging.info(message)
        self.lineNotify(message)

        exeTimer1 = 0
        exeTimer5 = 0
        while True:
            logging.info('================================')
            exeMin = datetime.datetime.now().minute
            #1分ごとに基準ラインを更新
            if exeMin + 1 > exeTimer1 or exeMin + 1 < exeTimer1:
                exeTimer1 = exeMin + 1
                logging.info("Renewing candleSticks")
                try:
                    if "H" in self.candleTerm:
                        candleStick = self.cryptowatch.getCandlestick(480, "3600")
                    else:
                        candleStick = self.cryptowatch.getCandlestick(480, "60")
                except:
                    logging.error("Unknown error happend when you requested candleStick")

                if self.candleTerm == None:
                    df_candleStick = self.fromListToDF(candleStick)
                else:
                    df_candleStick = self.processCandleStick(candleStick, self.candleTerm)

                #ラインの算出
                entryLowLine, entryHighLine = self.calculateLines(df_candleStick, self.entryTerm, self.rangePercent, self.rangePercentTerm)
                closeLowLine, closeHighLine = self.calculateLines(df_candleStick, self.closeTerm, self.rangePercent, self.rangePercentTerm)
                #現在レンジ相場かどうか．
                isRange = self.isRange(df_candleStick, self.rangeTerm, self.rangeTh)
            else:
                pass

            #直近約定件数30件の高値と安値
            high = max([self.executions[-1-i]["price"] for i in range(30)])
            low = min([self.executions[-1-i]["price"] for i in range(30)])
            #売り買い判定
            judgement = self.judgeForLoop(high, low, entryHighLine, entryLowLine, closeHighLine, closeLowLine)

            #取引所のヘルスチェック
            boardState = self.order.getboardstate()
            serverHealth = True
            permitHealth1 = ["NORMAL", "BUSY", "VERY BUSY"]
            permitHealth2 = ["NORMAL", "BUSY", "VERY BUSY", "SUPER BUSY"]
            if (boardState["health"] in permitHealth1) and boardState["state"] == "RUNNING" and self.healthCheck:
                pass
            elif (boardState["health"] in permitHealth2) and boardState["state"] == "RUNNING" and not self.healthCheck:
                pass
            else:
                serverHealth = False
                logging.info('Server is %s/%s. Do not order.', boardState["health"], boardState["state"])

            #ログ出力
            logging.info('high:%s low:%s isRange:%s', high, low, isRange[-1])
            logging.info('entryHighLine:%s entryLowLine:%s', entryHighLine[-1], entryLowLine[-1])
            logging.info('closeLowLine:%s closeHighLine:%s', closeLowLine[-1], closeHighLine[-1])
            logging.info('Server Health is:%s State is:%s', boardState["health"], boardState["state"])
            if pos == 1:
                logging.info('position : Long(Price:%s)',lastPositionPrice)
            elif pos == -1:
                logging.info('position : Short(Price:%s)',lastPositionPrice)
            else:
                logging.info("position : None")

            #ここからエントリー，クローズ処理
            if pos == 0 and not isRange[-1] and serverHealth:
                #ロングエントリー
                if judgement[0]:
                    logging.info("Long entry order")
                    orderId = self.order.market(size=lot, side="BUY")
                    pos += 1
                    childOrder = self.order.getexecutions(orderId["child_order_acceptance_id"])
                    best_ask = childOrder[0]["price"]
                    message = "Long entry. Lot:{}, Price:{}".format(lot, best_ask)
                    self.lineNotify(message)
                    logging.info(message)
                    lastPositionPrice = best_ask
                #ショートエントリー
                elif judgement[1]:
                    logging.info("Short entry order")
                    orderId = self.order.market(size=lot,side="SELL")
                    pos -= 1
                    childOrder = self.order.getexecutions(orderId["child_order_acceptance_id"])
                    best_bid = childOrder[0]["price"]
                    message = "Short entry. Lot:{}, Price:{}, ".format(lot, best_bid)
                    self.lineNotify(message)
                    logging.info(message)
                    lastPositionPrice = best_bid

            elif pos == 1:
                #ロングクローズ
                if judgement[2]:
                    logging.info("Long close order")
                    orderId = self.order.market(size=lot,side="SELL")
                    pos -= 1
                    childOrder = self.order.getexecutions(orderId["child_order_acceptance_id"])
                    best_bid = childOrder[0]["price"]
                    plRange = best_bid - lastPositionPrice
                    pl.append(pl[-1] + plRange * lot)
                    message = "Long close. Lot:{}, Price:{}, pl:{}".format(lot, best_bid, pl[-1])
                    fileName = self.describePLForNotification(pl, df_candleStick)
                    self.lineNotify(message,fileName)
                    logging.info(message)

                    #一定以上の値幅を取った場合，次の10トレードはロットを1/10に落とす．
                    if plRange > self.waitTh:
                        waitTerm = self.waitTerm
                        lot = round(originalLot/10,3)
                    if waitTerm > 0:
                        waitTerm -= 1
                        lot = round(originalLot/10,3)
                    if waitTerm == 0:
                         lot = originalLot

            elif pos == -1:
                #ショートクローズ
                if judgement[3]:
                    logging.info("Short close order")
                    orderId = self.order.market(size=lot, side="BUY")
                    pos += 1
                    childOrder = self.order.getexecutions(orderId["child_order_acceptance_id"])
                    best_ask = childOrder[0]["price"]
                    plRange = lastPositionPrice - best_ask
                    pl.append(pl[-1] + plRange * lot)
                    message = "Short close. Lot:{}, Price:{}, pl:{}".format(lot, best_ask, pl[-1])
                    fileName = self.describePLForNotification(pl, df_candleStick)
                    self.lineNotify(message,fileName)
                    logging.info(message)

                    #一定以上の値幅を取った場合，次の10トレードはロットを1/10に落とす．
                    if plRange > self.waitTh:
                        waitTerm = self.waitTerm
                        lot = round(originalLot/10,3)
                    if waitTerm > 0:
                        waitTerm -= 1
                        lot = round(originalLot/10,3)
                    if waitTerm == 0:
                         lot = originalLot

            #クローズしたと同時にエントリーシグナルが出ていた場合にドテン売買
            if pos == 0 and not isRange[-1] and serverHealth:
                #ロングエントリー
                if judgement[0]:
                    logging.info("Long doten entry order")
                    orderId = self.order.market(size=lot, side="BUY")
                    pos += 1
                    childOrder = self.order.getexecutions(orderId["child_order_acceptance_id"])
                    best_ask = childOrder[0]["price"]
                    message = "Long entry. Lot:{}, Price:{}".format(lot, best_ask)
                    self.lineNotify(message)
                    logging.info(message)
                    lastPositionPrice = best_ask
                #ショートエントリー
                elif judgement[1]:
                    logging.info("Short doten entry order")
                    orderId = self.order.market(size=lot,side="SELL")
                    pos -= 1
                    childOrder = self.order.getexecutions(orderId["child_order_acceptance_id"])
                    best_bid = childOrder[0]["price"]
                    message = "Short entry. Lot:{}, Price:{}, ".format(lot, best_bid)
                    self.lineNotify(message)
                    logging.info(message)
                    lastPositionPrice = best_bid

            if (exeMin + 1 > exeTimer5 or exeMin + 1 < exeTimer5) and exeMin % 5 == 0:
                exeTimer5 = exeMin + 1
                message = "Waiting for channelbreaking."
                logging.info(message)

            time.sleep(2)

    def executionsProcess(self):
        """
        pubnubで価格を取得する場合の処理（基本的に不要．）
        """
        channels = ["lightning_executions_FX_BTC_JPY"]
        executions = self.executions
        class BFSubscriberCallback(SubscribeCallback):
            def message(self, pubnub, message):
                execution = message.message
                for i in execution:
                    executions.append(i)

        config = PNConfiguration()
        config.subscribe_key = 'sub-c-52a9ab50-291b-11e5-baaa-0619f8945a4f'
        config.reconnect_policy = PNReconnectionPolicy.EXPONENTIAL
        config.ssl = False
        config.set_presence_timeout(60)
        pubnub = PubNubTornado(config)
        listener = BFSubscriberCallback()
        pubnub.add_listener(listener)
        pubnub.subscribe().channels(channels).execute()
        pubnubThread = threading.Thread(target=pubnub.start)
        pubnubThread.start()
