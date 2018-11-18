#_*_ coding: utf-8 _*_
#https://sshuhei.com

import json
import logging
import logging.handlers
import time
import itertools
from src import channel
from hyperopt import fmin, tpe, hp

def describe(params):
    i, j, k, l, m, cost, mlMode, fileName = params

    channelBreakOut = channel.ChannelBreakOut()
    channelBreakOut.entryTerm = i[0]
    channelBreakOut.closeTerm = i[1]
    channelBreakOut.rangeTh = j[0]
    channelBreakOut.rangeTerm = j[1]
    channelBreakOut.waitTerm = k[0]
    channelBreakOut.waitTh = k[1]
    channelBreakOut.rangePercent = l[0]
    channelBreakOut.rangePercentTerm = l[1]
    channelBreakOut.candleTerm = str(m) + "T"
    channelBreakOut.cost = cost
    channelBreakOut.fileName = fileName
    logging.info("===========Test pattern===========")
    logging.info('candleTerm:%s',channelBreakOut.candleTerm)
    logging.info('entryTerm:%s closeTerm:%s',channelBreakOut.entryTerm,channelBreakOut.closeTerm)
    logging.info('rangePercent:%s rangePercentTerm:%s',channelBreakOut.rangePercent,channelBreakOut.rangePercentTerm)
    logging.info('rangeTerm:%s rangeTh:%s',channelBreakOut.rangeTerm,channelBreakOut.rangeTh)
    logging.info('waitTerm:%s waitTh:%s',channelBreakOut.waitTerm,channelBreakOut.waitTh)
    logging.info("===========Backtest===========")
    pl, profitFactor, maxLoss, winPer, ev = channelBreakOut.describeResult()

    if "PFDD" in mlMode:
        result = profitFactor/maxLoss
    elif "PL" in mlMode:
        result = -pl
    elif "PF" in mlMode:
        result = -profitFactor
    elif "DD" in mlMode:
        result = -maxLoss
    elif "WIN" in mlMode:
        result = -winPer
    elif "EV" in mlMode:
        result = -ev

    logging.info("===========Assessment===========")
    logging.info('Result:%s',result)
    return result

def optimization(cost, fileName, hyperopt, mlMode, showTradeDetail):
    #optimizeList.jsonの読み込み
    f = open('config/optimizeList.json', 'r', encoding="utf-8")
    config = json.load(f)
    entryAndCloseTerm = config["entryAndCloseTerm"]
    rangeThAndrangeTerm = config["rangeThAndrangeTerm"]
    waitTermAndwaitTh = config["waitTermAndwaitTh"]
    rangePercentList = config["rangePercentList"]
    linePattern = config["linePattern"]
    termUpper = config["termUpper"]
    candleTerm  = config["candleTerm"]

    if "COMB" in linePattern:
        entryAndCloseTerm = list(itertools.product(range(2,termUpper), range(2,termUpper)))

    total = len(entryAndCloseTerm) * len(rangeThAndrangeTerm) * len(waitTermAndwaitTh) * len(rangePercentList) * len(candleTerm)

    logging.info('Total pattern:%s Searches:%s',total,hyperopt)
    logging.info("======Optimization start======")
    #hyperoptによる最適値の算出
    space = [hp.choice('i',entryAndCloseTerm), hp.choice('j',rangeThAndrangeTerm), hp.choice('k',waitTermAndwaitTh), hp.choice('l',rangePercentList), hp.choice('m',candleTerm), cost, mlMode, fileName]
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
    channelBreakOut.candleTerm = str(candleTerm[result['m']]) + "T"
    channelBreakOut.cost = cost
    channelBreakOut.fileName = fileName
    channelBreakOut.showTradeDetail = showTradeDetail
    logging.info("======Best pattern======")
    logging.info('candleTerm:%s mlMode:%s',channelBreakOut.candleTerm,mlMode)
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
    f = open('config/config.json', 'r', encoding="utf-8")
    config = json.load(f)
    logging.info('cost:%s mlMode:%s fileName:%s',config["cost"],config["mlMode"],config["fileName"])

    #最適化
    start = time.time()
    optimization(cost=config["cost"], fileName=config["fileName"], hyperopt=config["hyperopt"], mlMode=config["mlMode"], showTradeDetail=config["showTradeDetail"])
    logging.info('total processing time: %s', time.time() - start)
