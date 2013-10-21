import time
import urllib.request
import urllib.error
import urllib.parse
import config
import logging
from fiatconverter import FiatConverter


class Market(object):
    def __init__(self, to_currency="USD", from_currency="BTC", update_rate=60):
        self.to_currency = to_currency
        self.from_currency = from_currency
        self.depth_updated = 0
        self.update_rate = update_rate
        self.trade_fee = 0
        self.fc = FiatConverter()
        self.fc.update()

    @property
    def name(self):
        return self.__class__.__name__

    def get_depth(self):
        timediff = time.time() - self.depth_updated
        if timediff > self.update_rate:
            self.ask_update_depth()
        timediff = time.time() - self.depth_updated
        if timediff > config.market_expiration_time:
            logging.warning('Market: %s order book is expired' % self.name)
            self.depth = {'asks': [{'price': 0, 'amount': 0}], 'bids': [{'price': 0, 'amount': 0}]}
        if self.depth['bids'][0]['price'] > self.depth['asks'][0]['price']:
            logging.warning('Market: %s order book is invalid (bid>ask : quotation is stopped ?)' % self.name)
            self.depth = {'asks': [{'price': 0, 'amount': 0}], 'bids': [{'price': 0, 'amount': 0}]}
        return self.depth

    def convert_to_usd(self):
        if self.to_currency == "USD":
            return
        for direction in ("asks", "bids"):
            for order in self.depth[direction]:
                order["price"] = self.fc.convert(order["price"], self.to_currency, "USD")

    def ask_update_depth(self):
        try:
            self.update_depth()
            self.convert_to_usd()
            self.depth_updated = time.time()
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            logging.error("HTTPError, can't update market: %s" % self.name)
        except Exception as e:
            logging.error("Can't update market: %s - %s" % (self.name, str(e)))

    def get_ticker(self):
        depth = self.get_depth()
        res = {'ask': 0, 'bid': 0}
        if len(depth['asks']) > 0 and len(depth["bids"]) > 0:
            res = {'ask': depth['asks'][0],
                   'bid': depth['bids'][0]}
        return res

    ## Abstract methods
    def update_depth(self):
        pass

    def buy(self, price, amount):
        pass

    def sell(self, price, amount):
        pass
