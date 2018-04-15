#_*_ coding: utf-8 _*_
#https://sshuhei.com

import json
import logging
import time
import itertools
from src import channel
from concurrent.futures import ProcessPoolExecutor

def describe(params):
    i, j, k, l, candleTerm, cost, fileName, core = params

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

    #テスト
    pl, profitFactor = channelBreakOut.describeResult()
    return [pl, profitFactor, i, l, j, k]

def optimization(candleTerm, cost, fileName, core):
    #optimizeList.jsonの読み込み
    f = open('optimizeList.json', 'r', encoding="utf-8")
    config = json.load(f)
    entryAndCloseTerm = config["entryAndCloseTerm"]
    rangeThAndrangeTerm = config["rangeThAndrangeTerm"]
    waitTermAndwaitTh = config["waitTermAndwaitTh"]
    rangePercentList = config["rangePercentList"]
    total = len(entryAndCloseTerm) * len(rangeThAndrangeTerm) * len(waitTermAndwaitTh) * len(rangePercentList)

    paramList = []
    params = []
    for i, j, k, l in itertools.product(entryAndCloseTerm, rangeThAndrangeTerm, waitTermAndwaitTh, rangePercentList):
        params.append([i, j, k, l, candleTerm, cost, fileName, core])

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
                paramList.append(result)
                logging.info('[%s/%s] result:%s',len(paramList),total,paramList[-1])

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
    optimization(candleTerm=config["candleTerm"], cost=config["cost"], fileName=config["fileName"], core=config["core"])
    logging.info('total processing time: %s', time.time() - start)
