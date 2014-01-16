import logging
#from arbitrage import config
import config
import time
from .observer import Observer
from Pubnub import Pubnub


class pubnubmessager(Observer):
    def __init__(self):
      self.pn = Pubnub(config.pubnub_pubkey, config.pubnub_subkey)
      print("Started")

    def opportunity(self, profit, volume, buyprice, kask, sellprice, kbid, perc,
                    weighted_buyprice, weighted_sellprice):
        if profit > config.profit_thresh and perc > config.perc_thresh:
            message = "profit: %f USD with volume: %f BTC - buy at %.4f (%s) sell at %.4f (%s) ~%.2f%%" % (profit, volume, buyprice, kask, sellprice, kbid, perc)
            self.pn.publish({'channel' : config.pubnub_topic, 'message' :{ 'msg' : message}})
