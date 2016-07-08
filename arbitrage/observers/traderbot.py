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
    def __init__(self):
        self.clients = {
            # "HaobtcCNY": haobtccny.PrivateHaobtcCNY(config.HAOBTC_API_KEY, config.HAOBTC_SECRET_TOKEN),
            "OKCoinCNY": okcoincny.PrivateOkCoinCNY(config.OKCOIN_API_KEY, config.OKCOIN_SECRET_TOKEN),
            "HuobiCNY": huobicny.PrivateHuobiCNY(config.HUOBI_API_KEY, config.HUOBI_SECRET_TOKEN),
            # "BrokerCNY": brokercny.PrivateBrokerCNY(),
        }

        self.reverse_profit_thresh = config.reverse_profit_thresh
        self.reverse_perc_thresh = config.reverse_perc_thresh
        self.profit_thresh = config.profit_thresh
        self.perc_thresh = config.perc_thresh
        self.trade_wait = 15 * 1  # in seconds
        self.last_trade = 0

        self.init_btc = {'OKCoinCNY':500, 'HuobiCNY':500}

        self.stage0_percent = config.stage0_percent
        self.stage1_percent = config.stage1_percent
        self.last_bid_price = 0
        self.trend_up = True

        self.exchange = 'OKCoinCNY'

    def begin_opportunity_finder(self, depths):
        self.potential_trades = []

        # Update client balance
        self.update_balance()

    def update_balance(self):
        for kclient in self.clients:
            self.clients[kclient].get_info()

    def end_opportunity_finder(self):
        if not self.potential_trades:
            return
        self.potential_trades.sort(key=lambda x: x[0])
        # Execute only the best (more profitable)
        self.execute_trade(*self.potential_trades[0][1:])

    def get_min_tradeable_volume(self, buyprice, cny_bal, btc_bal):
        min1 = float(cny_bal) * (1. - config.balance_margin) / buyprice
        min2 = float(btc_bal) * (1. - config.balance_margin)

        return min(min1, min2)

    def opportunity(self, profit, volume, buyprice, kask, sellprice, kbid, perc,
                    weighted_buyprice, weighted_sellprice):
        if kask not in self.clients:
            logging.warn("Can't automate this trade, client not available: %s" % kask)
            return
        if kbid not in self.clients:
            logging.warn("Can't automate this trade, client not available: %s" % kbid)
            return

        arbitrage_max_volume = config.max_tx_volume
        if profit < self.reverse_profit_thresh and perc < self.reverse_perc_thresh:
            logging.info("Profit or profit percentage(%0.4f/%0.4f) lower than thresholds(%s/%s)" 
                            % (profit, perc, self.reverse_profit_thresh, self.reverse_perc_thresh))
            arbitrage_max_volume = config.reverse_max_tx_volume

            if self.clients[kbid].btc_balance < self.stage0_percent*self.init_btc[kbid]:
                return
                logging.info("Buy @%s/%0.2f and sell @%s/%0.2f %0.2f BTC" % (kask, buyprice, kbid, sellprice, volume))
                logging.info("%s fund:%s < %s * init:%s, reverse", kbid, self.clients[kbid].btc_balance, self.stage0_percent, self.init_btc[kbid])
                ktemp = kbid
                kbid = kask
                kask = ktemp
            elif self.clients[kask].btc_balance < self.stage1_percent*self.init_btc[kask]:
                logging.info("Buy @%s/%0.2f and sell @%s/%0.2f %0.2f BTC" % (kask, buyprice, kbid, sellprice, volume))
                logging.info("%s fund:%s init:%s, go on", kask, self.clients[kask].btc_balance, self.init_btc[kask])
            else:
                logging.debug("wait for higher")
                return
        elif profit > self.profit_thresh and perc > self.perc_thresh:
            logging.info("Profit or profit percentage(%0.4f/%0.4f) higher than thresholds(%s/%s)" 
                            % (profit, perc, self.profit_thresh, self.perc_thresh))    

            arbitrage_max_volume = config.max_tx_volume
        else:
            logging.debug("Profit or profit percentage(%0.4f/%0.4f) out of scope thresholds(%s~%s/%s~%s)" 
                            % (profit, perc, self.reverse_profit_thresh, self.profit_thresh, self.perc_thresh, self.reverse_perc_thresh))
            return

        if perc > 20:  # suspicous profit, added after discovering btc-central may send corrupted order book
            logging.warn("Profit=%f seems malformed" % (perc, ))
            return

        max_volume = self.get_min_tradeable_volume(buyprice,
                                                   self.clients[kask].cny_balance,
                                                   self.clients[kbid].btc_balance)
        volume = min(volume, max_volume, arbitrage_max_volume)
        if volume < config.min_tx_volume:
            logging.warn("Can't automate this trade, minimum volume transaction"+
                         " not reached %f/%f" % (volume, config.min_tx_volume))
            return

        current_time = time.time()
        if current_time - self.last_trade < self.trade_wait:
            logging.warn("Can't automate this trade, last trade " +
                         "occured %.2f seconds ago" %
                         (current_time - self.last_trade))
            return

        self.potential_trades.append([profit, volume, kask, kbid,
                                      weighted_buyprice, weighted_sellprice,
                                      buyprice, sellprice])

    def execute_trade(self, volume, kask, kbid, weighted_buyprice,
                      weighted_sellprice, buyprice, sellprice):
        volume = float('%0.2f' % volume)

        if self.clients[kask].cny_balance < volume*buyprice*10:
            logging.warn("%s cny is insufficent" % kask)
            return
 
        if self.clients[kbid].btc_balance < volume*10:
            logging.warn("%s btc is insufficent" % kbid)
            return

        logging.info("Fire:Buy @%s/%0.2f and sell @%s/%0.2f %0.2f BTC" % (kask, buyprice, kbid, sellprice, volume))

        # update trend
        if self.last_bid_price < buyprice:
            self.trend_up = True
        else:
            self.trend_up = False

        logging.info("trend is %s[%s->%s]", "up, buy then sell" if self.trend_up else "down, sell then buy", self.last_bid_price, buyprice)
        self.last_bid_price = buyprice

        # trade
        if self.trend_up:
            result = self.clients[kask].buy(volume, buyprice)
            if result == False:
                logging.warn("Buy @%s %f BTC failed" % (kask, volume))
                return

            self.last_trade = time.time()

            result = self.clients[kbid].sell(volume, sellprice)
            if result == False:
                logging.warn("Sell @%s %f BTC failed" % (kbid, volume))
                result = self.clients[kask].sell(volume, buyprice)
                if result == False:
                    logging.warn("2nd sell @%s %f BTC failed" % (kask, volume))
                    return
                return
        else:

            result = self.clients[kbid].sell(volume, sellprice)
            if result == False:
                logging.warn("Sell @%s %f BTC failed" % (kbid, volume))
                return
                
            self.last_trade = time.time()

            result = self.clients[kask].buy(volume, buyprice)
            if result == False:
                logging.warn("Buy @%s %f BTC failed" % (kask, volume))
                result = self.clients[kbid].buy(volume, sellprice)
                if result == False:
                    logging.warn("2nd buy @%s %f BTC failed" % (kbid, volume))
                    return
                return

