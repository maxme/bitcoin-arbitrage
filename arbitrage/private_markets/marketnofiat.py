# Copyright (C) 2013, Maxime Biais <maxime@biais.org>

import logging
from arbitrage import config

class TradeException(Exception):
    pass

class GetInfoException(Exception):
    pass

class MarketNoFiat:
    def __init__(self):
        self.name = self.__class__.__name__
        self.pair = config.pair
        pair_names = str.split(self.pair, "_")
        self.pair1_name = str.upper(pair_names[0])
        self.pair2_name = str.upper(pair_names[1])

    def __str__(self):
        return "%s: %s" % (self.name, str({self.pair1_name: self.pair1_balance,
                                           self.pair2_name: self.pair2_balance
                                           }))

    def buy(self, amount, price):
        logging.info("Buy %f %s at %f %s @%s" % (amount,self.pair1_name,
                     price,self.pair2_name,self.name))
        self._buy(amount, price)


    def sell(self, amount, price):
        logging.info("Sell %f %s at %f %s @%s" % (amount,self.pair1_name,
                     price,self.pair2_name,self.name))
        self._sell(amount, price)

    def _buy(self, amount, price):
        raise NotImplementedError("%s.sell(self, amount, price)" % self.name)

    def _sell(self, amount, price):
        raise NotImplementedError("%s.sell(self, amount, price)" % self.name)

    def deposit(self):
        raise NotImplementedError("%s.sell(self, amount, price)" % self.name)

    def withdraw(self, amount, address):
        raise NotImplementedError("%s.sell(self, amount, price)" % self.name)

    def get_info(self):
        raise NotImplementedError("%s.sell(self, amount, price)" % self.name)
