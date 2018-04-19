#_*_ coding: utf-8 _*_
#https://sshuhei.com

import os.path
import json
import logging
import time
import itertools
import pandas as pd
from src import channel
from concurrent.futures import ProcessPoolExecutor

def eq(a, b):
    return (a == b) | (pd.isnull(a) & pd.isnull(b))

def describe(params):
    i, j, k, l, candleTerm, cost, fileName, core, useBlackList = params

    channelBreakOut = channel.ChannelBreakOut()
    channelBreakOut.entryTerm = i[0]
    channelBreakOut.closeTerm = i[1]
    channelBreakOut.rangeTh = j[0]
    channelBreakOut.rangeTerm = j[1]
    channelBreakOut.waitTerm = k[0]
    channelBreakOut.waitTh = k[1]
    channelBreakOut.rangePercent = l[0]
    channelBreakOut.rangePercentTerm = l[1]
    channelBreakOut.candleTerm = candleTerm
    channelBreakOut.cost = cost
    channelBreakOut.fileName = fileName
    if core == 1:
        logging.info('================================')
        logging.info('entryTerm:%s closeTerm:%s rangePercent:%s rangePercentTerm:%s rangeTerm:%s rangeTh:%s waitTerm:%s waitTh:%s',i[0],i[1],l[0],l[1],j[1],j[0],k[0],k[1])
    else:
        pass

    # ブラックリスト判定
    is_blacklist = False
    if useBlackList:
        bl = read_blacklist()
        co = bl.columns.values
        is_blacklist = ((bl[co[0]] == candleTerm) &
                        (eq(bl[co[1]], i[0])) &
                        (eq(bl[co[2]], i[1])) &
                        (eq(bl[co[3]], j[0])) &
                        (eq(bl[co[4]], j[1])) &
                        (eq(bl[co[5]], k[1])) &
                        (eq(bl[co[6]], k[0])) &
                        (eq(bl[co[7]], l[0])) &
                        (eq(bl[co[8]], l[1]))).any()

    if is_blacklist:
        pl = 0
        profitFactor = 0
    else:
        #テスト
        pl, profitFactor, maxLoss, winPer = channelBreakOut.describeResult()
    return [pl, profitFactor, i, l, j, k, is_blacklist]

def optimization(candleTerm, cost, fileName, core, useBlackList):
    #optimizeList.jsonの読み込み
    f = open('optimizeList.json', 'r', encoding="utf-8")
    config = json.load(f)
    entryAndCloseTerm = config["entryAndCloseTerm"]
    rangeThAndrangeTerm = config["rangeThAndrangeTerm"]
    waitTermAndwaitTh = config["waitTermAndwaitTh"]
    rangePercentList = config["rangePercentList"]
    linePattern = config["linePattern"]
    randomUpper = config["randomUpper"]

    if "R" in linePattern:
        entryAndCloseTerm = list(itertools.product(range(2,randomUpper), range(2,randomUpper)))

    total = len(entryAndCloseTerm) * len(rangeThAndrangeTerm) * len(waitTermAndwaitTh) * len(rangePercentList)

    paramList = []
    params = []
    for i, j, k, l in itertools.product(entryAndCloseTerm, rangeThAndrangeTerm, waitTermAndwaitTh, rangePercentList):
        params.append([i, j, k, l, candleTerm, cost, fileName, core, useBlackList])

    black_list = read_blacklist()
    if core == 1:
        # 同期処理
        for param in params:
            result = describe(param)
            paramList.append(result)
            logging.info('[%s/%s]',len(paramList),total)
    else:
        # 非同期処理
        with ProcessPoolExecutor(max_workers=core) as executor:
            for result in executor.map(describe, params):
                skiped = '(skip)' if result[6] == True else ''
                paramList.append(result)
                logging.info('[%s/%s] result%s:%s',len(paramList),total,skiped,paramList[-1])
                # ブラックリスト追加
                if (useBlackList == True) & (result[0] < 0) & (result[6] == False):
                    new_bl = pd.DataFrame(
                        [[candleTerm, result[2][0], result[2][1], result[4][0], result[4][1], result[5][1], result[5][0], result[3][0], result[3][0]]], columns=black_list.columns.values)
                    black_list = black_list.append(new_bl)
    # ブラックリスト書き込み
    if useBlackList: black_list.to_csv('blacklist.csv', index=False, sep=',')

    pF = [i[1] for i in paramList]
    pL = [i[0] for i in paramList]
    logging.info("======Optimization finished======")
    logging.info('Search pattern :%s', len(paramList))
    logging.info("Parameters:")
    logging.info("[entryTerm, closeTerm], [rangePercent, rangePercentTerm], [rangeTh, rangeTerm], [waitTerm, waitTh]")
    logging.info("ProfitFactor max:")
    logging.info(paramList[pF.index(max(pF))])
    logging.info("PL max:")
    logging.info(paramList[pL.index(max(pL))])
    message = "Optimization finished.\n ProfitFactor max:{}\n PL max:{}".format(paramList[pF.index(max(pF))], paramList[pL.index(max(pL))])
    channel.ChannelBreakOut().lineNotify(message)

    #config.json設定用ログ
    print("*********PF max*********")
    print("PL", paramList[pF.index(max(pF))][0])
    print("PF", paramList[pF.index(max(pF))][1])
    print("    \"entryTerm\" : ", paramList[pF.index(max(pF))][2][0], ",", sep="")
    print("    \"closeTerm\" : ", paramList[pF.index(max(pF))][2][1], ",", sep="")
    if paramList[pF.index(max(pF))][3][0] is None:
        print("    \"rangePercent\" : ", "null,", sep="")
    else:
        print("    \"rangePercent\" : ", paramList[pF.index(max(pF))][3][0], ",", sep="")
    if paramList[pF.index(max(pF))][3][1] is None:
        print("    \"rangePercentTerm\" : ", "null,", sep="")
    else:
        print("    \"rangePercentTerm\" : ", paramList[pF.index(max(pF))][3][1], ",", sep="")
    if paramList[pF.index(max(pF))][4][1] is None:
        print("    \"rangeTerm\" : ", "null,", sep="")
    else:
        print("    \"rangeTerm\" : ", paramList[pF.index(max(pF))][4][1], ",", sep="")
    if paramList[pF.index(max(pF))][4][0] is None:
        print("    \"rangeTh\" : ", "null,", sep="")
    else:
        print("    \"rangeTh\" : ", paramList[pF.index(max(pF))][4][0], ",", sep="")
    print("    \"waitTerm\" : ", paramList[pF.index(max(pF))][5][0], ",", sep="")
    print("    \"waitTh\" : ", paramList[pF.index(max(pF))][5][1], ",", sep="")
    print("    \"candleTerm\" : \"", candleTerm, "\",", sep="")

    print("*********PL max*********")
    print("PL", paramList[pL.index(max(pL))][0])
    print("PF", paramList[pL.index(max(pL))][1])
    print("    \"entryTerm\" : ", paramList[pL.index(max(pL))][2][0], ",", sep="")
    print("    \"closeTerm\" : ", paramList[pL.index(max(pL))][2][1], ",", sep="")
    if paramList[pL.index(max(pL))][3][0] is None:
        print("    \"rangePercent\" : ", "null,", sep="")
    else:
        print("    \"rangePercent\" : ", paramList[pL.index(max(pL))][3][0], ",", sep="")
    if paramList[pL.index(max(pL))][3][1] is None:
        print("    \"rangePercentTerm\" : ", "null,", sep="")
    else:
        print("    \"rangePercentTerm\" : ", paramList[pL.index(max(pL))][3][1], ",", sep="")
    if paramList[pL.index(max(pL))][4][1] is None:
        print("    \"rangeTerm\" : ", "null,", sep="")
    else:
        print("    \"rangeTerm\" : ", paramList[pL.index(max(pL))][4][1], ",", sep="")
    if paramList[pL.index(max(pL))][4][0] is None:
        print("    \"rangeTh\" : ", "null,", sep="")
    else:
        print("    \"rangeTh\" : ", paramList[pL.index(max(pL))][4][0], ",", sep="")
    print("    \"waitTerm\" : ", paramList[pL.index(max(pL))][5][0], ",", sep="")
    print("    \"waitTh\" : ", paramList[pL.index(max(pL))][5][1], ",", sep="")
    print("    \"candleTerm\" : \"", candleTerm, "\",", sep="")

def read_blacklist():
    if os.path.exists('blacklist.csv'):
        return pd.read_csv('blacklist.csv', header=0, sep=',')
    else:
        return pd.read_csv('blacklist_default.csv', header=0, sep=',')

if __name__ == '__main__':
    #logging設定
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    logfile=logging.handlers.TimedRotatingFileHandler(
        filename = 'log/optimization.log',
        when = 'midnight'
    )
    logfile.setLevel(logging.INFO)
    logfile.setFormatter(logging.Formatter(
        fmt='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'))
    logging.getLogger('').addHandler(logfile)
    logging.info('Wait...')

    #config.jsonの読み込み
    f = open('config.json', 'r', encoding="utf-8")
    config = json.load(f)
    logging.info('candleTerm:%s cost:%s core:%s fileName:%s',config["candleTerm"],config["cost"],config["core"],config["fileName"])

    #最適化
    start = time.time()
    optimization(candleTerm=config["candleTerm"], cost=config["cost"], fileName=config["fileName"], core=config["core"], useBlackList=config["useBlackList"])
    logging.info('total processing time: %s', time.time() - start)
