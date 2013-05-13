# Copyright (C) 2013, Maxime Biais <maxime@biais.org>

import urllib.request
import sys
import json
import logging
import time


class FiatConverter:
    __shared_state = {}
    rate_exchange_url = "http://rate-exchange.appspot.com/currency?from=%s&to=%s"

    def __init__(self):
        """USD is used as pivot"""
        self.__dict__ = self.__shared_state
        self.rates = {
            "USD": 1,
            "EUR": 0.77,
            "CNY": 6.15,
            "SEK": 6.6,
        }
        self.update_delay = 60 * 60 # every hour
        self.last_update = 0
        self.bank_fee = 0.007 # bank fee

    def get_currency_pair(self, code_from, code_to):
        url = self.rate_exchange_url % (code_from, code_to)
        res = urllib.request.urlopen(url)
        data = json.loads(res.read().decode('utf8'))
        rate = 0
        if "rate" in data:
            rate = data["rate"] * (1.0 - self.bank_fee)
        else:
            logging.error("Can't update fiat conversion rate: %s", url)
        return rate

    def update_currency_pair(self, code_to):
        if code_to == "USD":
            return
        code_from = "USD"
        rate = self.get_currency_pair(code_from, code_to)
        if rate:
            self.rates[code_to] = rate

    def update(self):
        timediff = time.time() - self.last_update
        if timediff < self.update_delay:
            return
        self.last_update = time.time()
        for currency in self.rates:
            self.update_currency_pair(currency)

    def convert(self, price, code_from, code_to):
        self.update()
        rate_from = self.rates[code_from]
        rate_to = self.rates[code_to]
        return price / rate_from * rate_to


if __name__ == "__main__":
    fc = FiatConverter()
    print(fc.convert(12., "USD", "EUR"))
    print(fc.convert(12., "EUR", "USD"))
    print(fc.rates)
