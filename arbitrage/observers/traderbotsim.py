import logging
import config
from .observer import Observer
from private_markets import mtgox
from private_markets import bitcoincentral
from .traderbot import TraderBot
import json


class MockMarket(object):
    def __init__(self, name, fee=0, balances=None, persistent=True):
        self.name = name
        self.filename = "traderbot-sim-" + name + ".json"
        self.balances = balances
        self.fee = fee
        self.persistent = persistent
        
        if not self.balances:
            self.balances = {
                "USD": 500.,
                "BTC": 15.,
                "LTC": 100.,
            }
        
        if self.persistent:
            try:
                self.load()
            except IOError:
                pass

    def execute(self, trade):
        self.balances[trade.from_currency] -= trade.from_volume
        self.balances[trade.to_currency] += trade.to_volume
        if self.persistent:
            self.save()

    def load(self):
        self.balances = json.load(open(self.filename, "r"))

    def save(self):
        json.dump(self.balances, open(self.filename, "w"))

    def balance(self, currency):
        return self.balances[currency]

    def balance_total(self, price):
        return self.usd_balance + self.btc_balance * price

    def get_info(self):
        pass


class TraderBotSim(TraderBot):
    def __init__(self):
        self.mtgox = MockMarket("mtgox", 0.006)  # 0.6% fee
        self.btcentral = MockMarket("bitcoin-central", 0.00489)
        self.intersango = MockMarket("intersango", 0.0065)
        self.bitcoin24 = MockMarket("bitcoin24", 0)
        self.bitstamp = MockMarket("bitstamp", 0.005)  # 0.5% fee
        self.campbx = MockMarket("campbx", 0)
        self.btce = MockMarket("btce", 0)

        self.clients = {
            "MtGox": self.mtgox,
            "Bitcentral": self.btcentral,
            "Intersango": self.intersango,
            "Bitcoin24": self.bitcoin24,
            "Bitstamp": self.bitstamp,
            "CampBX": self.campbx,
            "Btce": self.btce
        }
        self.profit_thresh = 1  # in EUR
        self.perc_thresh = 0.6  # in %
        self.trade_wait = 120
        self.last_trade = 0

    def total_balance(self, price):
        market_balances = [i.balance_total(
            price) for i in set(self.clients.values())]
        return sum(market_balances)

if __name__ == "__main__":
    t = TraderBotSim()
    print(t.total_balance(33))
