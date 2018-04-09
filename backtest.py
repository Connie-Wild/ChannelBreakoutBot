#_*_ coding: utf-8 _*_
#https://sshuhei.com

import json
import logging
import channel

if __name__ == '__main__':
    #logging設定
    logging.basicConfig(
        filename='channelBreakOut.log',
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p')
    console=logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(
        fmt='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p'))
    logging.getLogger('').addHandler(console)
    logging.info('Wait...')

    #config.jsonの読み込み
    f = open('config.json', 'r')
    config = json.load(f)

    #channelBreakOut設定値
    channelBreakOut = channel.ChannelBreakOut()
    channelBreakOut.entryTerm = config["entryTerm"]
    channelBreakOut.closeTerm = config["closeTerm"]
    channelBreakOut.rangePercent = config["rangePercent"]
    channelBreakOut.rangePercentTerm = config["rangePercentTerm"]
    channelBreakOut.rangeTerm = config["rangeTerm"]
    channelBreakOut.rangeTh = config["rangeTh"]
    channelBreakOut.waitTerm = config["waitTerm"]
    channelBreakOut.waitTh = config["waitTh"]
    channelBreakOut.candleTerm = config["candleTerm"]
    channelBreakOut.cost = config["cost"]
    channelBreakOut.fileName = config["fileName"]
    channelBreakOut.showFigure = config["showFigure"]

    #バックテスト
    channelBreakOut.describeResult(entryTerm=channelBreakOut.entryTerm, closeTerm=channelBreakOut.closeTerm, rangeTh=channelBreakOut.rangeTh, rangeTerm=channelBreakOut.rangeTerm, originalWaitTerm=channelBreakOut.waitTerm, waitTh=channelBreakOut.waitTh, candleTerm=channelBreakOut.candleTerm, showFigure=channelBreakOut.showFigure, cost=channelBreakOut.cost, rangePercent=channelBreakOut.rangePercent, rangePercentTerm=channelBreakOut.rangePercentTerm)
