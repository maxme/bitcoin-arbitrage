import logging
from arbitrage import config
from arbitrage.observers.observer import Observer
import time

class Logger(Observer):
    def __init__(self):
        self.last_log_time = time.time()
        self.prev_perc = 0
    def opportunity(self, profit, volume, buyprice, kask, sellprice, kbid, perc,
                    weighted_buyprice, weighted_sellprice):

        pair_names = str.split(config.pair, "_")
        pair1_name = str.upper(pair_names[0])
        pair2_name = str.upper(pair_names[1])

        if time.time() - self.last_log_time > 1 or perc > self.prev_perc:
            logging.info("profit: %f %s with volume: %f %s - buy from %s sell to %s ~%.2f%%" \
            	% (profit, pair2_name, volume, pair1_name, kask, kbid, perc))
            self.last_log_time = time.time()
            self.prev_perc = perc
