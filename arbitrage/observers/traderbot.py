import logging
import config
import time
from .observer import Observer
from .emailer import send_email
from fiatconverter import FiatConverter
from private_markets import bitstampusd,haobtccny,huobicny,okcoincny, brokercny
import os, time
import sys
import traceback

class TraderBot(Observer):
    exchange = 'HaobtcCNY'
    out_dir = 'trade_history/'

    def __init__(self):
        self.clients = {
            # TODO: move that to the config file
            "HaobtcCNY": haobtccny.PrivateHaobtcCNY(config.HAOBTC_API_KEY, config.HAOBTC_SECRET_TOKEN),
            "OKCoinCNY": okcoincny.PrivateOkCoinCNY(config.OKCOIN_API_KEY, config.OKCOIN_SECRET_TOKEN),
            "HuobiCNY": huobicny.PrivateHuobiCNY(config.HUOBI_API_KEY, config.HUOBI_SECRET_TOKEN),
            "BrokerCNY": tradercny.PrivateBrokerCNY(),
        }

        self.profit_thresh = config.profit_thresh
        self.perc_thresh = config.perc_thresh
        self.trade_wait = 10 * 1  # in seconds
        self.last_trade = 0
        self.cny_balance = 0
        self.btc_balance = 0
        self.cny_frozen = 0
        self.btc_frozen = 0
        self.cny_total = 0
        self.btc_total = 0
       
        try:
            os.mkdir(self.out_dir)
        except:
            pass

    def begin_opportunity_finder(self, depths):
        self.potential_trades = []

        # Update client balance
        self.update_balance()

        # get price
        try:
            bid_price = int(depths[self.exchange]["bids"][0]['price'])
            ask_price = int(depths[self.exchange]["asks"][0]['price'])
        except  Exception as ex:
            logging.warn("exception depths:%s" % ex)
            t,v,tb = sys.exc_info()
            print(t,v)
            traceback.print_exc()

            # logging.warn(depths)
            return

        if bid_price == 0 or ask_price == 0:
            logging.warn("exception ticker")
            return

        self.cny_total = self.cny_balance_total(bid_price)
        self.btc_total = self.btc_balance_total(ask_price)

        self.update_trade_history(time.time(), bid_price, self.cny_total, self.btc_total)


    def end_opportunity_finder(self):
        if not self.potential_trades:
            return
        self.potential_trades.sort(key=lambda x: x[0])
        # Execute only the best (more profitable)
        self.execute_trade(*self.potential_trades[0][1:])

    def get_min_tradeable_volume(self, buyprice, cny_bal, btc_bal):
        min1 = float(cny_bal) / ((1. + config.balance_margin) * buyprice)
        min2 = float(btc_bal) / (1. + config.balance_margin)
        return min(min1, min2)

    def update_balance(self):
        self.cny_balance = 0
        self.btc_balance = 0
        self.cny_frozen = 0
        self.btc_frozen = 0
        for kclient in self.clients:
            self.clients[kclient].get_info()
            self.cny_balance += self.clients[kclient].cny_balance
            self.btc_balance += self.clients[kclient].btc_balance
            
            self.cny_frozen += self.clients[kclient].cny_frozen
            self.btc_frozen += self.clients[kclient].btc_frozen

    def cny_balance_total(self, price):
        return self.cny_balance + self.cny_frozen+ (self.btc_balance + self.btc_frozen)* price
    
    def btc_balance_total(self, price):
        return self.btc_balance + self.btc_frozen  + (self.cny_balance +self.cny_frozen ) / (price*1.0)


    def update_trade_history(self, time, price, cny, btc):
        filename = self.out_dir + 'arbitrage.csv'
        need_header = False

        if not os.path.exists(filename):
            need_header = True

        fp = open(filename, 'a+')

        if need_header:
            fp.write("timestamp, price, cny, btc\n")

        fp.write(("%d") % time +','+("%.2f") % price+','+("%.2f") % cny+','+ str(("%.4f") % btc) +'\n')
        fp.close()

    def opportunity(self, profit, volume, buyprice, kask, sellprice, kbid, perc,
                    weighted_buyprice, weighted_sellprice):
        if kask not in self.clients:
            logging.warn("[TraderBot] Can't automate this trade, client not available: %s" % kask)
            return
        if kbid not in self.clients:
            logging.warn("[TraderBot] Can't automate this trade, client not available: %s" % kbid)
            return

        if profit < self.profit_thresh or perc < self.perc_thresh:
            logging.info("[TraderBot] Profit or profit percentage(%0.4f/%0.4f) lower than thresholds(%s/%s)" 
                            % (profit, perc, self.profit_thresh, self.perc_thresh))
            return
        else:
            logging.info("[TraderBot] Profit or profit percentage(%0.4f/%0.4f) higher than thresholds(%s/%s)" 
                            % (profit, perc, self.profit_thresh, self.perc_thresh))    
        
        if perc > 20:  # suspicous profit, added after discovering btc-central may send corrupted order book
            logging.warn("[TraderBot]Profit=%f seems malformed" % (perc, ))
            return

        max_volume = self.get_min_tradeable_volume(buyprice,
                                                   self.clients[kask].cny_balance,
                                                   self.clients[kbid].btc_balance)

        logging.info("volume:%s max_volume:%0.4f", volume, max_volume)

        volume = min(volume, max_volume, config.max_tx_volume)
        if volume < config.min_tx_volume:
            logging.warn("[TraderBot]Can't automate this trade, minimum volume transaction"+
                         " not reached %f/%f" % (volume, config.min_tx_volume))
            logging.warn("Balance on %s: %f CNY / %s: %f BTC"
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
        logging.info("[TraderBot]Buy @%s %f BTC and sell @%s" % (kask, volume, kbid))

        volume = float(("%0.4f") % volume)
        buyprice = (buyprice)
        result = self.clients[kask].buy(volume, buyprice)
        if result == False:
            logging.warn("[TraderBot]Buy @%s %f BTC failed" % (kask, volume))
            return
            
        sellprice = (sellprice)
        result = self.clients[kbid].sell(volume, sellprice)
        if result == False:
            logging.warn("[TraderBot]Sell @%s %f BTC failed" % (kbid, volume))
            return

        if config.send_trade_mail:
            send_email("[TraderBot]Bought @%s %f BTC and sold @%s" % (kask, volume, kbid),
                   "weighted_buyprice=%f weighted_sellprice=%f" % (weighted_buyprice, weighted_sellprice))
