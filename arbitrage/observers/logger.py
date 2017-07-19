import logging
from arbitrage.observers.observer import ObserverBase

LOG = logging.getLogger(__name__)

_format = "profit: %f USD, vol: %f BTC, %s [%s] -> %s [%s], ~%.2f%%"


class Logger(ObserverBase):
    def opportunity(self, profit, volume, buyprice, kask, sellprice, kbid,
                    perc, weighted_buyprice, weighted_sellprice):
        """Log opportunity"""

        buy_exchange, buy_currency = kask[:-3], kask[-3:]
        sell_exchange, sell_currency = kbid[:-3], kbid[-3:]
        LOG.info(_format % (profit,
                            volume,
                            buy_exchange.upper(),
                            buy_currency,
                            sell_exchange.upper(),
                            sell_currency,
                            perc))
