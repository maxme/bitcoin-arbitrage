# Copyright (C) 2013, Maxime Biais <maxime@biais.org>

import logging
from fiatconverter import FiatConverter

class TradeException(Exception):
    pass

class Market:
    def __init__(self):
        self.name = self.__class__.__name__
        self.balances = {}

    def __str__(self):
        return "%s: %s" % (self.name, str(self.balances))

    def execute(self, trade):
        logging.debug("[%s] Got command \"%s\"" % (
            self.__class__.__name__, str(trade))
        )
        if trade.type == "buy":
            self._buy(trade)
        elif trade.type == "sell":
            self._sell(trade)

    def _buy(self, trade):
        raise NotImplementedError("%s.sell(self, amount, price)" % self.name)

    def _sell(self, trade):
        raise NotImplementedError("%s.sell(self, amount, price)" % self.name)

    def deposit(self):
        raise NotImplementedError("%s.sell(self, amount, price)" % self.name)

    def withdraw(self, amount, address):
        raise NotImplementedError("%s.sell(self, amount, price)" % self.name)

    def get_info(self):
        raise NotImplementedError("%s.sell(self, amount, price)" % self.name)
