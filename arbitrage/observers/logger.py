import logging
from arbitrage import config
from arbitrage.observers.observer import Observer


class Logger(Observer):
    def opportunity(self, profit, volume, buyprice, kask, sellprice, kbid, perc,
                    weighted_buyprice, weighted_sellprice):

        pair_names = str.split(config.pair, "_")
        pair1_name = str.upper(pair_names[0])
        pair2_name = str.upper(pair_names[1])
        logging.info("profit: %f %s with volume: %f %s - buy from %s sell to %s ~%.2f%%" \
        	% (profit, pair2_name, volume, pair1_name, kask, kbid, perc))
