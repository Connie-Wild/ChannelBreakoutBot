#_*_ coding: utf-8 _*_
#https://sshuhei.com

import json
import logging
from src import channel

def optimization(candleTerm, fileName):
    entryAndCloseTerm = [(2,2),(3,2),(2,3),(3,3),(4,2),(2,4),(4,3),(3,4),(4,4),(5,2),(2,5),(5,3),(3,5),(5,4),(4,5),(5,5),(10,10)]
    rangeThAndrangeTerm = [(None,3),(5000,3),(10000,3),(None,5),(5000,5),(10000,5),(None,10),(5000,10),(10000,10),(None,15),(5000,15),(10000,15),(None,None)]
    waitTermAndwaitTh = [(0,0),(3,10000),(3,15000),(3,20000),(5,10000),(5,15000),(5,20000),(10,10000),(10,15000),(10,20000),(15,10000),(15,15000),(15,20000)]
    rangePercentList = [(None,None),(1.5,5),(2,5),(2.5,5)]
    total = len(entryAndCloseTerm) * len(rangeThAndrangeTerm) * len(waitTermAndwaitTh) * len(rangePercentList)

    paramList = []
    for i in entryAndCloseTerm:
        for j in rangeThAndrangeTerm:
            for k in waitTermAndwaitTh:
                for l in rangePercentList:
                    channelBreakOut = channel.ChannelBreakOut()
                    channelBreakOut.entryTerm = i[0]
                    channelBreakOut.closeTerm = i[1]
                    channelBreakOut.rangeTh = j[0]
                    channelBreakOut.rangeTerm = j[1]
                    channelBreakOut.waitTerm = k[0]
                    channelBreakOut.waitTh = k[1]
                    channelBreakOut.rangePercent = l[0]
                    channelBreakOut.rangePercentTerm = l[1]
                    channelBreakOut.fileName = fileName
                    channelBreakOut.candleTerm = candleTerm
                    logging.info('================================')
                    logging.info('[%s/%s] entryTerm:%s closeTerm:%s rangePercent:%s rangePercentTerm:%s rangeTerm:%s rangeTh:%s waitTerm:%s waitTh:%s candleTerm:%s',len(paramList)+1,total,i[0],i[1],l[0],l[1],j[1],j[0],k[0],k[1],candleTerm)
                    #テスト
                    pl, profitFactor =  channelBreakOut.describeResult()
                    paramList.append([pl,profitFactor, i,l,j,k])

    pF = [i[1] for i in paramList]
    pL = [i[0] for i in paramList]
    logging.info("======Search finished======")
    logging.info('Search pattern :%s', len(paramList))
    logging.info("Parameters:")
    logging.info("(entryTerm, closeTerm), (rangePercent, rangePercentTerm), (rangeTh, rangeTerm), (waitTerm, waitTh)")
    logging.info("ProfitFactor max:")
    logging.info(paramList[pF.index(max(pF))])
    logging.info("PL max:")
    logging.info(paramList[pL.index(max(pL))])

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
    optimization(candleTerm=config["candleTerm"], fileName=config["fileName"])
