import logging
import config
import time
from .observer import Observer
from .emailer import send_email
from fiatconverter import FiatConverter
from private_markets import bitstampusd,haobtccny,huobicny,okcoincny
from .emailer import send_email

class TraderBot(Observer):
    def __init__(self):
        self.clients = {
            # TODO: move that to the config file
            "HaobtcCNY": haobtccny.PrivateHaobtcCNY(),
            "OKCoinCNY": okcoincny.PrivateOkCoinCNY(),
            "HuobiCNY": huobicny.PrivateHuobiCNY(),
        }

        self.profit_thresh = config.profit_thresh
        self.perc_thresh = config.perc_thresh
        self.trade_wait = 120 * 1  # in seconds
        self.last_trade = 0

    def begin_opportunity_finder(self, depths):
        self.potential_trades = []

    def end_opportunity_finder(self):
        if not self.potential_trades:
            return
        self.potential_trades.sort(key=lambda x: x[0])
        # Execute only the best (more profitable)
        self.execute_trade(*self.potential_trades[0][1:])

    def get_min_tradeable_volume(self, buyprice, cny_bal, btc_bal):
        min1 = float(cny_bal) / ((1. + config.balance_margin) * buyprice)
        min2 = float(btc_bal) / (1. + config.balance_margin)
        return min(min1, min2)/ 0.95

    def update_balance(self):
        for kclient in self.clients:
            self.clients[kclient].get_info()

    def opportunity(self, profit, volume, buyprice, kask, sellprice, kbid, perc,
                    weighted_buyprice, weighted_sellprice):
        if kask not in self.clients:
            logging.warn("[TraderBot] Can't automate this trade, client not available: %s" % kask)
            return
        if kbid not in self.clients:
            logging.warn("[TraderBot] Can't automate this trade, client not available: %s" % kbid)
            return

        if profit < self.profit_thresh or perc < self.perc_thresh:
            logging.verbose("[TraderBot] Profit or profit percentage(%0.4f/%0.4f) lower than thresholds(%s/%s)" 
                            % (profit, perc, self.profit_thresh, self.perc_thresh))
            return
        else:
            logging.verbose("[TraderBot] Profit or profit percentage(%0.4f/%0.4f) higher than thresholds(%s/%s)" 
                            % (profit, perc, self.profit_thresh, self.perc_thresh))    
        
        if perc > 20:  # suspicous profit, added after discovering btc-central may send corrupted order book
            logging.warn("Profit=%f seems malformed" % (perc, ))
            return

        # Update client balance
        self.update_balance()

        max_volume = self.get_min_tradeable_volume(buyprice,
                                                   self.clients[kask].cny_balance,
                                                   self.clients[kbid].btc_balance)

        volume = min(volume, max_volume, config.max_tx_volume)
        if volume < config.min_tx_volume:
            logging.warn("Can't automate this trade, minimum volume transaction"+
                         " not reached %f/%f" % (volume, config.min_tx_volume))
            logging.warn("Balance on %s: %f CNY - Balance on %s: %f BTC"
                         % (kask, self.clients[kask].cny_balance, kbid,
                            self.clients[kbid].btc_balance))
            return

        current_time = time.time()
        if current_time - self.last_trade < self.trade_wait:
            logging.warn("[TraderBot] Can't automate this trade, last trade " +
                         "occured %.2f seconds ago" %
                         (current_time - self.last_trade))
            return
        self.potential_trades.append([profit, volume, kask, kbid,
                                      weighted_buyprice, weighted_sellprice,
                                      buyprice, sellprice])

    def watch_balances(self):
        pass

    def execute_trade(self, volume, kask, kbid, weighted_buyprice,
                      weighted_sellprice, buyprice, sellprice):
        self.last_trade = time.time()
        logging.info("Buy @%s %f BTC and sell @%s" % (kask, volume, kbid))

        buyprice = int(buyprice)+1
        result = self.clients[kask].buy(volume, buyprice)
        if result == False:
            logging.warn("Buy @%s %f BTC failed" % (kask, volume))
            return
            
        sellprice = int(sellprice)-1
        result = self.clients[kbid].sell(volume, sellprice)
        if result == False:
            logging.warn("Sell @%s %f BTC failed" % (kbid, volume))
            return

        if config.send_trade_mail:
            send_email("Bought @%s %f BTC and sold @%s" % (kask, volume, kbid),
                   "weighted_buyprice=%f weighted_sellprice=%f" % (weighted_buyprice, weighted_sellprice))
