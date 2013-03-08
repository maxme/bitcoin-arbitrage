import logging
import config
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
        print self.mtgox
        print self.btcentral

    def opportunity(self, profit, volume, buyprice, kask, sellprice, kbid, perc):
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

        # Everything's ok, ask for transactions
        self.clients[kask].buy(volume)
        self.clients[kbid].sell(volume)




