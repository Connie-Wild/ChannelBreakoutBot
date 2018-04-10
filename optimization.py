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
        logging.info('entryTerm:%s closeTerm:%s rangePercent:%s rangePercentTerm:%s rangeTerm:%s rangeTh:%s waitTerm:%s waitTh:%s candleTerm:%s cost:%s',i[0],i[1],l[0],l[1],j[1],j[0],k[0],k[1],candleTerm,cost)
    else:
        pass

    #テスト
    pl, profitFactor = channelBreakOut.describeResult()
    return [pl, profitFactor, i, l, j, k]

def optimization(candleTerm, cost, fileName, core):
    entryAndCloseTerm = [(2,2),(3,2),(2,3),(3,3),(4,2),(2,4),(4,3),(3,4),(4,4),(5,2),(2,5),(5,3),(3,5),(5,4),(4,5),(5,5),(10,10)]
    rangeThAndrangeTerm = [(None,3),(5000,3),(10000,3),(None,5),(5000,5),(10000,5),(None,10),(5000,10),(10000,10),(None,15),(5000,15),(10000,15),(None,None)]
    waitTermAndwaitTh = [(0,0),(3,10000),(3,15000),(3,20000),(5,10000),(5,15000),(5,20000),(10,10000),(10,15000),(10,20000),(15,10000),(15,15000),(15,20000)]
    rangePercentList = [(None,None),(1.5,5),(2,5),(2.5,5)]
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
                logging.info('[%s/%s]',len(paramList),total)

    pF = [i[1] for i in paramList]
    pL = [i[0] for i in paramList]
    logging.info("======Optimization finished======")
    logging.info('Search pattern :%s', len(paramList))
    logging.info("Parameters:")
    logging.info("(entryTerm, closeTerm), (rangePercent, rangePercentTerm), (rangeTh, rangeTerm), (waitTerm, waitTh)")
    logging.info("ProfitFactor max:")
    logging.info(paramList[pF.index(max(pF))])
    logging.info("PL max:")
    logging.info(paramList[pL.index(max(pL))])
    message = "Optimization finished.\n ProfitFactor max:{}\n PL max:{}".format(paramList[pF.index(max(pF))], paramList[pL.index(max(pL))])
    channel.ChannelBreakOut().lineNotify(message)

if __name__ == '__main__':
    #logging設定
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p')
    logfile=logging.handlers.TimedRotatingFileHandler(
        filename = 'log/optimization.log',
        when = 'D'
    )
    logfile.setLevel(logging.INFO)
    logfile.setFormatter(logging.Formatter(
        fmt='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p'))
    logging.getLogger('').addHandler(logfile)
    logging.info('Wait...')

    #config.jsonの読み込み
    f = open('config.json', 'r')
    config = json.load(f)

    #最適化
    start = time.time()
    optimization(candleTerm=config["candleTerm"], cost=config["cost"], fileName=config["fileName"], core=config["core"])
    logging.info('total processing time: %s', time.time() - start)
