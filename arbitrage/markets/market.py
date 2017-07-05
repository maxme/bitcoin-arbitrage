import logging
import time
import urllib.error
import urllib.parse
import urllib.request

from arbitrage.config import Configuration
from arbitrage.fiatconverter import FiatConverter
from arbitrage.registry import markets_registry

LOG = logging.getLogger(__name__)


class Plugin(type):
    """Dynamically add a class to the registry"""

    def __new__(mcs, clsname, bases, attrs):
        newclass = super(Plugin, mcs).__new__(mcs, clsname, bases, attrs)
        if not clsname.endswith('Base'):
            markets_registry[clsname] = newclass
        return newclass


class MarketBase(object, metaclass=Plugin):
    """"""

    def __init__(self, currency, config):
        self.name = self.__class__.__name__
        self.currency = currency
        self.depth_updated = 0
        self.config = config or Configuration()
        self.update_rate = self.config.default_market_update_rate
        self.depth = None
        self.fc = FiatConverter(config)
        self.fc.update()

    def set_config(self, config):
        self.config = config

    def get_depth(self):
        time_diff = time.time() - self.depth_updated
        if time_diff > self.update_rate:
            self.ask_update_depth()
        time_diff = time.time() - self.depth_updated
        if time_diff > self.config.market_expiration_time:
            LOG.warning('Market: %s order book is expired' % self.name)
            self.depth = {'asks': [{'price': 0, 'amount': 0}], 'bids': [
                {'price': 0, 'amount': 0}]}
        return self.depth

    def convert_to_usd(self):
        if self.currency == "USD":
            return
        for direction in ("asks", "bids"):
            for order in self.depth[direction]:
                order["price"] = self.fc.convert(order["price"], self.currency,
                                                 "USD")

    def ask_update_depth(self):
        try:
            self.update_depth()
            self.convert_to_usd()
            self.depth_updated = time.time()
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            LOG.exception("HTTPError, can't update market: %s" % self.name)
        except Exception as e:
            LOG.exception("Can't update market: %s - %s" % (self.name, str(e)))

    def get_ticker(self):
        depth = self.get_depth()
        res = {'ask': 0, 'bid': 0}
        if len(depth['asks']) > 0 and len(depth["bids"]) > 0:
            res = {'ask': depth['asks'][0],
                   'bid': depth['bids'][0]}
        return res

    def update_depth(self):
        pass

    def buy(self, price, amount):
        pass

    def sell(self, price, amount):
        pass
