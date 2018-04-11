#_*_ coding: utf-8 _*_
#https://sshuhei.com

import json
import logging
from src import channel

if __name__ == '__main__':
    #logging設定
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    logfile=logging.handlers.TimedRotatingFileHandler(
        filename = 'log/backtest.log',
        when = 'midnight'
    )
    logfile.setLevel(logging.INFO)
    logfile.setFormatter(logging.Formatter(
        fmt='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'))
    logging.getLogger('').addHandler(logfile)
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
    channelBreakOut.sendFigure = config["sendFigure"]
    channelBreakOut.showTradeDetail = config["showTradeDetail"]

    #バックテスト
    channelBreakOut.describeResult()
