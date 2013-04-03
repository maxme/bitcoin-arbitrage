import logging
from .observer import Observer


class Logger(Observer):
    def opportunity(self, profit, volume, buyprice, kask, sellprice, kbid, perc, weighted_buyprice, weighted_sellprice):
        logging.info("profit: %f EUR with volume: %f BTC - buy at %.4f (%s) sell at %.4f (%s) ~%.2f%%" %
                     (profit, volume, buyprice, kask, sellprice, kbid, perc))
