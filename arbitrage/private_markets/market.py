# Copyright (C) 2013, Maxime Biais <maxime@biais.org>

import logging
from fiatconverter import FiatConverter

class TradeException(Exception):
    pass

class Market:
    def __init__(self):
        self.name = self.__class__.__name__
        self.btc_balance = 0.
        self.eur_balance = 0.
        self.usd_balance = 0.
        self.cny_balance = 0.
        self.btc_frozen = 0.
        self.cny_frozen = 0.
        self.fc = FiatConverter()

    def __str__(self):
        return "%s: %s" % (self.name, str({"btc_balance": self.btc_balance,
                                           "cny_balance": self.cny_balance}))

    def buy(self, amount, price):
        """Orders are always priced in CNY"""
        local_currency_price = self.fc.convert(price, "CNY", self.currency)
        logging.verbose("Buy %f BTC at %f %s (%f CNY) @%s" % (amount,
                     local_currency_price, self.currency, price, self.name))
        return self._buy(amount, local_currency_price)


    def sell(self, amount, price):
        """Orders are always priced in CNY"""
        local_currency_price = self.fc.convert(price, "CNY", self.currency)
        logging.verbose("Sell %f BTC at %f %s (%f CNY) @%s" % (amount,
                     local_currency_price, self.currency, price, self.name))
        return self._sell(amount, local_currency_price)

    def buy_maker(self, amount, price):
        """Orders are always priced in CNY"""

        local_currency_price = self.fc.convert(price, "CNY", self.currency)
        local_currency_price = int(local_currency_price)
        logging.verbose("Buy maker %f BTC at %d %s (%d CNY) @%s" % (amount,
                     local_currency_price, self.currency, price, self.name))

        return self._buy_maker(amount, local_currency_price)


    def sell_maker(self, amount, price):
        """Orders are always priced in CNY"""
        local_currency_price = self.fc.convert(price, "CNY", self.currency)
        local_currency_price = int(local_currency_price)

        logging.verbose("Sell maker %f BTC at %d %s (%d CNY) @%s" % (amount,
                     local_currency_price, self.currency, price, self.name))

        return self._sell_maker(amount, local_currency_price)

    def get_order(self, order_id):
        return self._get_order(order_id)

    def cancel_order(self, order_id):
        return self._cancel_order(order_id)

    def cancel_all(self):
        return self._cancel_all()


    def _buy(self, amount, price):
        raise NotImplementedError("%s.buy(self, amount, price)" % self.name)

    def _sell(self, amount, price):
        raise NotImplementedError("%s.sell(self, amount, price)" % self.name)

    def _buy_maker(self, amount, price):
        raise NotImplementedError("%s.buy_maker(self, amount, price)" % self.name)

    def _sell_maker(self, amount, price):
        raise NotImplementedError("%s.sell_maker(self, amount, price)" % self.name)


    def _get_order(self, order_id):
        raise NotImplementedError("%s.get_order(self, order_id)" % self.name)

    def _cancel_order(self, order_id):
        raise NotImplementedError("%s.cancel_order(self, order_id)" % self.name)

    def _cancel_all(self):
        raise NotImplementedError("%s.cancel_all(self)" % self.name)

    def deposit(self):
        raise NotImplementedError("%s.sell(self, amount, price)" % self.name)

    def withdraw(self, amount, address):
        raise NotImplementedError("%s.sell(self, amount, price)" % self.name)

    def get_info(self):
        raise NotImplementedError("%s.sell(self, amount, price)" % self.name)
