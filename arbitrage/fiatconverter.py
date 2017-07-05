# Copyright (C) 2013, Maxime Biais <maxime@biais.org>

import urllib.request
import time
import logging

from arbitrage.config import Configuration

LOG = logging.getLogger(__name__)


class FiatConverter(object):
    __shared_state = {}
    rate_exchange_url = "http://download.finance.yahoo.com/" \
                        "d/quotes.csv?s=%s%s=X&f=sl1d1&e=.csv"

    def __init__(self, config=None):
        """USD is used as pivot"""
        self.__dict__ = self.__shared_state
        self.rates = {
            "USD": 1,
            "EUR": 0.77,
            "CNY": 6.15,
            "SEK": 6.6,
        }
        self.config = config or Configuration()
        self.last_update = 0
        self.update_delay = self.config.fiat_update_delay
        self.bank_fee = self.config.bank_fee

    def get_currency_pair(self, code_from, code_to):
        url = self.rate_exchange_url % (code_from, code_to)
        res = urllib.request.urlopen(url)
        data = res.read().decode('utf8').split(",")[1]
        rate = float(data) * (1.0 - self.bank_fee)
        return rate

    def update_currency_pair(self, code_to):
        if code_to == "USD":
            return
        code_from = "USD"
        rate = None
        try:
            rate = self.get_currency_pair(code_from, code_to)
        except urllib.error.HTTPError:
            LOG.error('Failed to get currency pair %s:%s' % (code_from,
                                                             code_to))
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
