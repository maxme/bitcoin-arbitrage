import logging
import config
import time
from observer import Observer
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
        self.profit_thresh = 5 # in EUR
        self.perc_thresh = 2 # in %
        self.trade_wait = 120 # in seconds
        self.last_trade = 0

    def opportunity(self, profit, volume, buyprice, kask, sellprice, kbid, perc, weighted_buyprice, weighted_sellprice):
        if profit < self.profit_thresh or perc < self.perc_thresh:
            return
        if kask not in self.clients:
            logging.warn("Can't automate this trade, client not available: %s" % (kask))
        if kbid not in self.clients:
            logging.warn("Can't automate this trade, client not available: %s" % (kbid))
        volume = min(config.max_tx_volume, volume)

        # Check balances
        if (volume * buyprice) * (1 + config.balance_margin) > self.clients[kask].eur_balance:
            logging.warn("Can't automate this trade, not enough money on: %s - need %f got %f" \
                         % (kask, (volume * buyprice) * (1 + config.balance_margin),
                         self.clients[kask].eur_balance))
            return
        if volume * (1 + config.balance_margin) > self.clients[kbid].btc_balance:
            logging.warn("Can't automate this trade, not enough money on: %s - need %f got %f" \
                         % (kbid, volume * (1 + config.balance_margin),
                         self.clients[kbid].btc_balance))
            return

        current_time = time.time()
        if current_time - self.last_trade < self.trade_wait:
            logging.warn("Can't automate this trade, last trade occured %s seconds ago" % (current_time - self.last_trade))
            return

        # Everything's ok, ask for transactions
        logging.info("Trader bot execute a transaction - profit: %f and perc: %f" % (profit, perc))
        self.execute_trade(volume, kask, kbid, weighted_buyprice, weighted_sellprice)

    def execute_trade(self, volume, kask, kbid, weighted_buyprice, weighted_sellprice):
        self.clients[kask].buy(volume)
        self.clients[kbid].sell(volume)





