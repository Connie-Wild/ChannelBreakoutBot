#_*_ coding: utf-8 _*_
#https://sshuhei.com

import json
import logging
import logging.handlers
from src import channel
import os

if __name__ == '__main__':
    #logging設定
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    logfile=logging.handlers.TimedRotatingFileHandler(
        filename = 'log/trade.log',
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

    #channelBreakOut設定値
    channelBreakOut = channel.ChannelBreakOut()
    channelBreakOut.lot = config["lotSize"]
    channelBreakOut.entryTerm = config["entryTerm"]
    channelBreakOut.closeTerm = config["closeTerm"]
    channelBreakOut.rangePercent = config["rangePercent"]
    channelBreakOut.rangePercentTerm = config["rangePercentTerm"]
    channelBreakOut.rangeTerm = config["rangeTerm"]
    channelBreakOut.rangeTh = config["rangeTh"]
    channelBreakOut.waitTerm = config["waitTerm"]
    channelBreakOut.waitTh = config["waitTh"]
    channelBreakOut.candleTerm = config["candleTerm"]
    channelBreakOut.sfdLimit = config["sfdLimit"]
    channelBreakOut.fileName = None

    # 約定履歴ファイルを引き継がない場合は削除
    if config["keepPosition"]==False :
        try:
            os.remove( 'log/orderhistory.csv' )
        except:
            pass

    #実働
    channelBreakOut.loop()
