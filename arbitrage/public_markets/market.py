import time
import urllib.request
import urllib.error
import urllib.parse
import logging
import sys
from arbitrage import config
from arbitrage.fiatconverter import FiatConverter
from arbitrage.utils import log_exception


class Market(object):
    def __init__(self, currency):
        self.name = self.__class__.__name__
        self.currency = currency
        self.depth_updated = 0
        self.update_rate = 60
        self.fc = FiatConverter()
        self.fc.update()

    def get_depth(self):
        timediff = time.time() - self.depth_updated
        if timediff > self.update_rate:
            self.ask_update_depth()
        timediff = time.time() - self.depth_updated
        if timediff > config.market_expiration_time:
            logging.warn("Market: %s order book is expired" % self.name)
            self.depth = {"asks": [{"price": 0, "amount": 0}], "bids": [{"price": 0, "amount": 0}]}
        return self.depth

    def convert_to_usd(self):
        if self.currency == "USD":
            return
        for direction in ("asks", "bids"):
            for order in self.depth[direction]:
                order["price"] = self.fc.convert(order["price"], self.currency, "USD")

    def ask_update_depth(self):
        try:
            self.update_depth()
            self.convert_to_usd()
            self.depth_updated = time.time()
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            logging.error("HTTPError, can't update market: %s" % self.name)
            log_exception(logging.DEBUG)
        except Exception as e:
            logging.error("Can't update market: %s - %s" % (self.name, str(e)))
            log_exception(logging.DEBUG)

    def get_ticker(self):
        depth = self.get_depth()
        res = {"ask": 0, "bid": 0}
        if len(depth["asks"]) > 0 and len(depth["bids"]) > 0:
            res = {"ask": depth["asks"][0], "bid": depth["bids"][0]}
        return res

    ## Abstract methods
    def update_depth(self):
        pass

    def buy(self, price, amount):
        pass

    def sell(self, price, amount):
        pass

    def _depth_pct(self,pct):
        bid1 = float(self.depth['bids'][0]['price'])
        ask1 = float(self.depth['asks'][0]['price'])
        fair = bid1*0.5 + ask1*0.5
        ceiling,floor = fair*(1+pct/100), fair*(1-pct/100)

        bid_sum = 0
        for bid in self.depth['bids']:
            if float(bid['price'])>floor:
                bid_sum += float(bid['amount'])
            else:
                break

        ask_sum = 0
        for ask in self.depth['asks']:
            if float(ask['price'])<ceiling:
                ask_sum += float(ask['amount'])
            else:
                break

        def _f(v):
            return int(v*100)/100

        return 'pct depth [bid, ask]: [ %s, %s ]'%( _f(bid_sum), _f(ask_sum) )

    def depth_1pct(self):
        return self._depth_pct(1)
    def depth_01pct(self):
        return self._depth_pct(0.1)

