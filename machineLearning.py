#_*_ coding: utf-8 _*_
#https://sshuhei.com

import json
import logging
import time
from src import channel
from hyperopt import fmin, tpe, hp

def describe(params):
    i, j, k, l, candleTerm, cost, mlMode, fileName = params

    cbo = channel.ChannelBreakOut()
    cbo.entryTerm = i[0]
    cbo.closeTerm = i[1]
    cbo.rangeTh = j[0]
    cbo.rangeTerm = j[1]
    cbo.waitTerm = k[0]
    cbo.waitTh = k[1]
    cbo.rangePercent = l[0]
    cbo.rangePercentTerm = l[1]
    cbo.candleTerm = candleTerm
    cbo.cost = cost
    cbo.fileName = fileName
    #formatStr = "entryT\t%s closeT\t%s rangeP\t%s rangePT\t%s rangeT\t%s rangeTh\t%s waitT\t%s waitTh\t%s"
    formatStr = "Pattern: %s\t%s\t%s\t%s\t%s\t%s\t%s\t%s"
    #logging.info("===========Test pattern===========")
    logging.info(formatStr,cbo.entryTerm,cbo.closeTerm,cbo.rangePercent,cbo.rangePercentTerm\
    ,cbo.rangeTerm,cbo.rangeTh,cbo.waitTerm,cbo.waitTh)
    pl, profitFactor, maxLoss, winPer = cbo.describeResult()
    if "PL" in mlMode:
        result = -pl
    elif "PF" in mlMode:
        result = -profitFactor
    elif "DD" in mlMode:
        result = -maxLoss
    elif "WIN" in mlMode:
        result = -winPer
    
    return result

def optimization(candleTerm, cost, fileName, hyperopt, mlMode, showTradeDetail):
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
    #hyperoptによる最適値の算出
    space = [hp.choice('i',entryAndCloseTerm), hp.choice('j',rangeThAndrangeTerm), hp.choice('k',waitTermAndwaitTh), hp.choice('l',rangePercentList), candleTerm, cost, mlMode, fileName]
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
    channelBreakOut.describeResult()

    #config.json設定用ログ
    print("======config======")
    print("    \"entryTerm\" : ", channelBreakOut.entryTerm, ",", sep="")
    print("    \"closeTerm\" : ", channelBreakOut.closeTerm, ",", sep="")
    if channelBreakOut.rangePercent is None:
        print("    \"rangePercent\" : ", "null,", sep="")
    else:
        print("    \"rangePercent\" : ", channelBreakOut.rangePercent, ",", sep="")
    if channelBreakOut.rangePercentTerm is None:
        print("    \"rangePercentTerm\" : ", "null,", sep="")
    else:
        print("    \"rangePercentTerm\" : ", channelBreakOut.rangePercentTerm, ",", sep="")
    if channelBreakOut.rangeTerm is None:
        print("    \"rangeTerm\" : ", "null,", sep="")
    else:
        print("    \"rangeTerm\" : ", channelBreakOut.rangeTerm, ",", sep="")
    if channelBreakOut.rangeTh is None:
        print("    \"rangeTh\" : ", "null,", sep="")
    else:
        print("    \"rangeTh\" : ", channelBreakOut.rangeTh, ",", sep="")
    print("    \"waitTerm\" : ", channelBreakOut.waitTerm, ",", sep="")
    print("    \"waitTh\" : ", channelBreakOut.waitTh, ",", sep="")
    print("    \"candleTerm\" : \"", channelBreakOut.candleTerm, "\",", sep="")
    print("==================")

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
    logging.info('candleTerm:%s cost:%s mlMode:%s fileName:%s',config["candleTerm"],config["cost"],config["mlMode"],config["fileName"])

    #最適化
    start = time.time()
    optimization(candleTerm=config["candleTerm"], cost=config["cost"], fileName=config["fileName"], hyperopt=config["hyperopt"], mlMode=config["mlMode"], showTradeDetail=config["showTradeDetail"])
    logging.info('total processing time: %s', time.time() - start)
