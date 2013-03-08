import logging
import sys
sys.path.append('../')
sys.path.append('.')
import config
from observer import Observer
from private_markets import mtgox
from private_markets import bitcoincentral
from traderbot import TraderBot
import json

class MockMarket(object):
    def __init__(self, name, fee=0, eur_balance=500., btc_balance=25., persistent=True):
        self.name = name
        self.filename = "traderbot-sim-" + name + ".json"
        self.eur_balance = eur_balance
        self.btc_balance = btc_balance
        self.fee = fee
        self.persistent = persistent
        if self.persistent:
            try:
                self.load()
            except IOError:
                pass

    def buy(self, volume, price):
        self.eur_balance -= price * volume
        self.btc_balance += volume - volume * self.fee
        if self.persistent:
            self.save()

    def sell(self, volume, price):
        self.btc_balance -= volume
        self.eur_balance += price * volume - price * volume * self.fee
        if self.persistent:
            self.save()

    def load(self):
        data = json.load(open(self.filename, "r"))
        self.eur_balance = data["eur"]
        self.btc_balance = data["btc"]

    def save(self):
        data = {'eur': self.eur_balance, 'btc': self.btc_balance}
        json.dump(data, open(self.filename, "w"))

    def balance_total(self, price):
        return self.eur_balance + self.btc_balance * price

class TraderBotSim(TraderBot):
    def __init__(self):
        self.mtgox = MockMarket("mtgox", 0.006) # 0.6% fee
        self.btcentral = MockMarket("bitcoin-central")
        self.clients = {
            "MtGoxEUR": self.mtgox,
            "MtGoxUSD": self.mtgox,
            "BitcoinCentralEUR": self.btcentral,
            "BitcoinCentralUSD": self.btcentral
            }
        self.profit_thresh = 1 # in EUR
        self.perc_thresh = 0.1 # in %
        self.trade_wait = 120
        self.last_trade = 0

    def total_balance(self, price):
        return self.mtgox.balance_total(price) + self.btcentral.balance_total(price)

    def execute_trade(self, volume, kask, kbid, weighted_buyprice, weighted_sellprice):
        self.clients[kask].buy(volume, weighted_buyprice)
        self.clients[kbid].sell(volume, weighted_sellprice)

if __name__ == "__main__":
    t = TraderBotSim()
    print t.total_balance(33)

