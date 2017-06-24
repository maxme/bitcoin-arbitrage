import logging
from arbitrage.observers.observer import Observer


class DetailedLogger(Observer):
    def opportunity(self, profit, volume, buyprice, kask, sellprice, kbid,
                    perc, weighted_buyprice, weighted_sellprice):
        params = (profit, volume, buyprice, kask, sellprice, kbid, perc)
        logging.info(
            "profit: %f USD with volume: %f BTC - buy at %.4f (%s) sell at "
            "%.4f (%s) ~%.2f%%" % params
        )
