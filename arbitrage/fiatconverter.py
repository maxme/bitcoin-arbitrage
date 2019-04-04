# Copyright (C) 2013-2019, Maxime Biais <maxime@bia.is>

import urllib.request
import sys
import xml.sax
import logging
import time


class XmlHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.currentTag = ""
        self.rates = {}

    def startElement(self, tag, attributes):
        if "currency" in attributes and "rate" in attributes:
            self.rates[attributes["currency"]] = float(attributes["rate"])

    def endElement(self, tag):
        pass

    def characters(self, content):
        pass


class FiatConverter:
    __shared_state = {}
    # Europa.eu is the official european central bank
    rate_exchange_url = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"

    def __init__(self):
        """USD is used as pivot"""
        self.__dict__ = self.__shared_state
        self.rates = {
            "USD": 1,
            "EUR": 0.77,
            "CNY": 6.15,
            "SEK": 6.6,
        }
        self.update_delay = 60 * 60 * 6  # every 6 hours
        self.last_update = 0
        self.bank_fee = 0.007  # TODO: bank fee
        self.handler = XmlHandler()

    def make_USD_pivot(self, rates):
        USDEUR = 1.0 / rates['USD']
        rates['EUR'] = USDEUR
        for k in rates:
            rates[k] = rates[k] * USDEUR
        return rates

    def update_pairs(self):
        url = self.rate_exchange_url
        res = urllib.request.urlopen(url)
        xml.sax.parseString(res.read().decode('utf8'), self.handler)
        self.rates = self.make_USD_pivot(self.handler.rates)

    def update(self):
        timediff = time.time() - self.last_update
        if timediff < self.update_delay:
            return
        self.last_update = time.time()
        self.update_pairs()

    def convert(self, price, code_from, code_to):
        self.update()
        rate_from = self.rates[code_from]
        rate_to = self.rates[code_to]
        return price / rate_from * rate_to


if __name__ == "__main__":
    fc = FiatConverter()
    print(fc.convert(12., "USD", "EUR"))
    print(fc.convert(12., "EUR", "USD"))
    print(fc.convert(fc.convert(12., "EUR", "USD"), "USD", "EUR"))
    print(fc.rates)
