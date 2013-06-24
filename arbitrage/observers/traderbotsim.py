import logging
import config
from .observer import Observer
from private_markets import mtgox
from private_markets import bitcoincentral
from .traderbot import TraderBot
import json


class MockMarket(object):
    def __init__(self, name, fee=0, usd_balance=500., btc_balance=15., persistent=True):
        self.name = name
        self.filename = "traderbot-sim-" + name + ".json"
        self.usd_balance = usd_balance
        self.btc_balance = btc_balance
        self.fee = fee
        self.persistent = persistent
        if self.persistent:
            try:
                self.load()
            except IOError:
                pass

    def buy(self, volume, price):
        logging.info("execute buy %f BTC @ %f on %s" %
                     (volume, price, self.name))
        self.usd_balance -= price * volume
        self.btc_balance += volume - volume * self.fee
        if self.persistent:
            self.save()

    def sell(self, volume, price):
        logging.info("execute sell %f BTC @ %f on %s" %
                     (volume, price, self.name))
        self.btc_balance -= volume
        self.usd_balance += price * volume - price * volume * self.fee
        if self.persistent:
            self.save()

    def load(self):
        data = json.load(open(self.filename, "r"))
        self.usd_balance = data["usd"]
        self.btc_balance = data["btc"]

    def save(self):
        data = {'usd': self.usd_balance, 'btc': self.btc_balance}
        json.dump(data, open(self.filename, "w"))

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
        self.clients = {
            "MtGoxEUR": self.mtgox,
            "MtGoxUSD": self.mtgox,
            "BitstampUSD": self.bitstamp,
        }
        self.profit_thresh = 1  # in EUR
        self.perc_thresh = 0.6  # in %
        self.trade_wait = 120
        self.last_trade = 0

    def total_balance(self, price):
        market_balances = [i.balance_total(
            price) for i in set(self.clients.values())]
        return sum(market_balances)

    def execute_trade(self, volume, kask, kbid, 
                      weighted_buyprice, weighted_sellprice,
                      buyprice, sellprice):
        self.clients[kask].buy(volume, buyprice)
        self.clients[kbid].sell(volume, sellprice)

if __name__ == "__main__":
    t = TraderBotSim()
    print(t.total_balance(33))
