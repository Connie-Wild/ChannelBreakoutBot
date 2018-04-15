#_*_ coding: utf-8 _*_
#https://sshuhei.com

import json
import logging
import time
from src import channel
from hyperopt import fmin, tpe, hp

def describe(params):
    i, j, k, l, candleTerm, cost, fileName = params

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
    logging.info("===========Test pattern===========")
    logging.info('entryTerm:%s closeTerm:%s',channelBreakOut.entryTerm,channelBreakOut.closeTerm)
    logging.info('rangePercent:%s rangePercentTerm:%s',channelBreakOut.rangePercent,channelBreakOut.rangePercentTerm)
    logging.info('rangeTerm:%s rangeTh:%s',channelBreakOut.rangeTerm,channelBreakOut.rangeTh)
    logging.info('waitTerm:%s waitTh:%s',channelBreakOut.waitTerm,channelBreakOut.waitTh)
    logging.info("===========Backtest===========")
    pl, profitFactor = channelBreakOut.describeResult()
    logging.info("===========Assessment===========")
    return -pl

def optimization(candleTerm, cost, fileName, hyperopt, showTradeDetail):
    #optimizeList.jsonの読み込み
    f = open('optimizeList.json', 'r', encoding="utf-8")
    config = json.load(f)
    entryAndCloseTerm = config["entryAndCloseTerm"]
    rangeThAndrangeTerm = config["rangeThAndrangeTerm"]
    waitTermAndwaitTh = config["waitTermAndwaitTh"]
    rangePercentList = config["rangePercentList"]
    total = len(entryAndCloseTerm) * len(rangeThAndrangeTerm) * len(waitTermAndwaitTh) * len(rangePercentList)

    logging.info('Total pattern:%s Searches:%s',total,hyperopt)
    logging.info("======Optimization start======")
    space = [hp.choice('i',entryAndCloseTerm), hp.choice('j',rangeThAndrangeTerm), hp.choice('k',waitTermAndwaitTh), hp.choice('l',rangePercentList), candleTerm, cost, fileName]
    result = fmin(describe,space,algo=tpe.suggest,max_evals=hyperopt)

    logging.info("======Optimization finished======")
    channelBreakOut = channel.ChannelBreakOut()
    channelBreakOut.entryTerm = entryAndCloseTerm[result['i']][0]
    channelBreakOut.closeTerm = entryAndCloseTerm[result['i']][1]
    channelBreakOut.rangeTh = rangeThAndrangeTerm[result['j']][0]
    channelBreakOut.rangeTerm = rangeThAndrangeTerm[result['j']][1]
    channelBreakOut.waitTerm = waitTermAndwaitTh[result['k']][0]
    channelBreakOut.waitTh = waitTermAndwaitTh[result['k']][1]
    channelBreakOut.rangePercent = rangePercentList[result['l']][0]
    channelBreakOut.rangePercentTerm = rangePercentList[result['l']][1]
    channelBreakOut.candleTerm = candleTerm
    channelBreakOut.cost = cost
    channelBreakOut.fileName = fileName
    channelBreakOut.showTradeDetail = showTradeDetail
    logging.info("======Best pattern======")
    logging.info('entryTerm:%s closeTerm:%s',channelBreakOut.entryTerm,channelBreakOut.closeTerm)
    logging.info('rangePercent:%s rangePercentTerm:%s',channelBreakOut.rangePercent,channelBreakOut.rangePercentTerm)
    logging.info('rangeTerm:%s rangeTh:%s',channelBreakOut.rangeTerm,channelBreakOut.rangeTh)
    logging.info('waitTerm:%s waitTh:%s',channelBreakOut.waitTerm,channelBreakOut.waitTh)
    logging.info("======Backtest======")
    pl, profitFactor = channelBreakOut.describeResult()

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
    logging.info('candleTerm:%s cost:%s fileName:%s',config["candleTerm"],config["cost"],config["fileName"])

    #最適化
    start = time.time()
    optimization(candleTerm=config["candleTerm"], cost=config["cost"], fileName=config["fileName"], hyperopt=config["hyperopt"], showTradeDetail=config["showTradeDetail"])
    logging.info('total processing time: %s', time.time() - start)
