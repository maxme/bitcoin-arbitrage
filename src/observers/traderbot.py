import logging
import config
import time
from .observer import Observer
from private_markets import mtgox
from private_markets import bitcoincentral


class TraderBot(Observer):
    def __init__(self):
        self.mtgox = mtgox.PrivateMtGox()
        self.btcentral = bitcoincentral.PrivateBitcoinCentral()
        self.clients = {
            "MtGoxEUR": self.mtgox,
            "MtGoxUSD": self.mtgox,
            "BitcoinCentralEUR": self.btcentral,
            "BitcoinCentralUSD": self.btcentral
        }
        self.profit_thresh = 5  # in EUR
        self.perc_thresh = 2  # in %
        self.trade_wait = 120  # in seconds
        self.last_trade = 0
        self.potential_trades = []

    def begin_opportunity_finder(self, depths):
        self.potential_trades = []

    def end_opportunity_finder(self):
        if not self.potential_trades:
            return
        self.potential_trades.sort(key=lambda x: x[0])
        # Execute only the best (more profitable)
        self.execute_trade(*self.potential_trades[0][1:])

    def get_min_tradeable_volume(self, buyprice, eur_bal, btc_bal):
        min1 = float(eur_bal) / ((1 + config.balance_margin) * buyprice)
        min2 = float(btc_bal) / (1 + config.balance_margin)
        return min(min1, min2)

    def update_balance(self):
        for kclient in self.clients:
            self.clients[kclient].get_info()

    def opportunity(self, profit, volume, buyprice, kask, sellprice, kbid, perc, weighted_buyprice, weighted_sellprice):
        if profit < self.profit_thresh or perc < self.perc_thresh:
            return
        if kask not in self.clients:
            logging.warn(
                "Can't automate this trade, client not available: %s" % (kask))
            return
        if kbid not in self.clients:
            logging.warn(
                "Can't automate this trade, client not available: %s" % (kbid))
            return
        volume = min(config.max_tx_volume, volume)

        # Update client balance
        self.update_balance()

        # maximum volume transaction with current balances
        max_volume = self.get_min_tradeable_volume(
            buyprice, self.clients[kask].eur_balance,
            self.clients[kbid].btc_balance)
        volume = min(volume, max_volume, config.max_tx_volume)

        if volume < config.min_tx_volume:
            logging.warn("Can't automate this trade, minimum volume transaction not reached %f/%f"
                         % (volume, config.min_tx_volume))
            return

        current_time = time.time()
        if current_time - self.last_trade < self.trade_wait:
            logging.warn("Can't automate this trade, last trade occured %s seconds ago" % (
                current_time - self.last_trade))
            return

        self.potential_trades.append(
            [profit, volume, kask, kbid, weighted_buyprice, weighted_sellprice])

    def watch_balances(self):
        pass

    def execute_trade(self, volume, kask, kbid, weighted_buyprice, weighted_sellprice):
        self.last_trade = time.time()
        self.clients[kask].buy(volume)
        self.clients[kbid].sell(volume)
