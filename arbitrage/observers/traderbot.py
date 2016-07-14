import logging
import config
import time
from .observer import Observer
from .emailer import send_email
from fiatconverter import FiatConverter
from private_markets import huobicny,okcoincny,brokercny
import os, time
import sys
import traceback
from .basicbot import BasicBot

class TraderBot(BasicBot):
    def __init__(self):
        super().__init__()

        self.clients = {
            # "HaobtcCNY": haobtccny.PrivateHaobtcCNY(config.HAOBTC_API_KEY, config.HAOBTC_SECRET_TOKEN),
            "OKCoinCNY": okcoincny.PrivateOkCoinCNY(config.OKCOIN_API_KEY, config.OKCOIN_SECRET_TOKEN),
            "HuobiCNY": huobicny.PrivateHuobiCNY(config.HUOBI_API_KEY, config.HUOBI_SECRET_TOKEN),
            "BrokerCNY": brokercny.PrivateBrokerCNY(),
        }

        self.reverse_profit_thresh = config.reverse_profit_thresh
        self.reverse_perc_thresh = config.reverse_perc_thresh
        self.profit_thresh = config.profit_thresh
        self.perc_thresh = config.perc_thresh
        self.trade_wait = config.trade_wait  # in seconds
        self.last_trade = 0

        self.init_btc = {'OKCoinCNY':500, 'HuobiCNY':500}

        self.stage0_percent = config.stage0_percent
        self.stage1_percent = config.stage1_percent
        self.last_bid_price = 0
        self.trend_up = True

        self.hedger = 'BrokerCNY'

    def begin_opportunity_finder(self, depths):
        self.potential_trades = []

        # Update client balance
        self.update_balance()

        self.check_order(depths)

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

    def check_order(self, depths):
        # update price

        # query orders
        if self.is_buying():
            buy_orders = self.get_orders('buy')
            buy_orders.sort(key=lambda x: x['price'], reverse=True)

            for buy_order in buy_orders:
                logging.debug(buy_order)
                result = self.clients[buy_order['market']].get_order(buy_order['id'])
                logging.debug (result)
                if not result:
                    logging.warn("get_order buy #%s failed" % (buy_order['id']))
                    continue

                if result['status'] == 'CLOSE' or result['status'] == 'CANCELED':
                    if result['status'] == 'CANCELED':
                        left_amount = result['amount']- result['deal_size']
                        logging.info("cancel ok %s result['price'] = %s, left_amount=%s" % (buy_order['market'], result['price'], left_amount))

                        self.clients[self.hedger].buy(left_amount, result['price'])

                    self.remove_order(buy_order['id'])
                else:
                    try:
                        ask_price =  int(depths[buy_order['market']]["asks"][0]['price'])
                    except  Exception as ex:
                        logging.warn("exception depths:%s" % ex)
                        traceback.print_exc()
                        continue

                    if abs(result['price']-ask_price) > config.arbitrage_cancel_price_diff:
                        left_amount = result['amount']- result['deal_size']
                        logging.info("Fire:cancel %s ask_price %s result['price'] = %s, left_amount=%s" % (buy_order['market'], ask_price, result['price'], left_amount))
                        self.cancel_order(buy_order['market'], 'buy', buy_order['id'])

        if self.is_selling():
            sell_orders = self.get_orders('sell')
            sell_orders.sort(key=lambda x: x['price'])

            for sell_order in self.get_orders('sell'):
                logging.debug(sell_order)
                result = self.clients[sell_order['market']].get_order(sell_order['id'])
                logging.debug (result)
                if not result:
                    logging.warn("get_order sell #%s failed" % (sell_order['id']))
                    continue

                if result['status'] == 'CLOSE' or result['status'] == 'CANCELED':
                    if result['status'] == 'CANCELED':
                        left_amount = result['amount']- result['deal_size']
                        logging.info("cancel ok %s result['price'] = %s, left_amount=%s" % (sell_order['market'], result['price'], left_amount))

                        self.clients[self.hedger].sell(left_amount, result['price'])

                    self.remove_order(sell_order['id'])
                else:
                    try:
                        bid_price = int(depths[sell_order['market']]["bids"][0]['price'])
                    except  Exception as ex:
                        logging.warn("exception depths:%s" % ex)
                        traceback.print_exc()
                        continue

                    if abs(result['price']-bid_price) > config.arbitrage_cancel_price_diff:
                        left_amount = result['amount']- result['deal_size']

                        logging.info("Fire:cancel %s bid_price %s result['price'] = %s,left_amount=%s" % (sell_order['market'], bid_price, result['price'], left_amount))
                        self.cancel_order(sell_order['market'], 'sell', sell_order['id'])

    def opportunity(self, profit, volume, buyprice, kask, sellprice, kbid, perc,
                    weighted_buyprice, weighted_sellprice):
        if kask not in self.clients:
            logging.warn("Can't automate this trade, client not available: %s" % kask)
            return
        if kbid not in self.clients:
            logging.warn("Can't automate this trade, client not available: %s" % kbid)
            return

        if self.buying_len() >= config.ARBITRAGER_BUY_QUEUE:
            logging.warn("Can't automate this trade, BUY queue is full: %s" % self.buying_len())
            return

        if self.selling_len() >= config.ARBITRAGER_SELL_QUEUE:
            logging.warn("Can't automate this trade, SELL queue is full: %s" % self.selling_len())
            return

        arbitrage_max_volume = config.max_tx_volume
        if profit < self.reverse_profit_thresh and perc < self.reverse_perc_thresh:
            logging.info("Profit or profit percentage(%0.4f/%0.4f) lower than thresholds(%s/%s)" 
                            % (profit, perc, self.reverse_profit_thresh, self.reverse_perc_thresh))
            arbitrage_max_volume = config.reverse_max_tx_volume

            if self.clients[kbid].btc_balance < self.stage0_percent*self.init_btc[kbid]:
                # return
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
            ktemp = kbid
            kbid = kask
            kask = ktemp
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

        if self.clients[kask].cny_balance < max(volume*buyprice*10, 31*buyprice):
            logging.warn("%s cny is insufficent" % kask)
            return
 
        if self.clients[kbid].btc_balance < max(volume*10, 31):
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
            result = self.new_order(kask, 'buy', maker_only=False, amount=volume, price=buyprice)
            if not result:
                logging.warn("Buy @%s %f BTC failed" % (kask, volume))
                return

            self.last_trade = time.time()

            result = self.new_order(kbid, 'sell', maker_only=False, amount= volume,  price=sellprice)
            if not result:
                logging.warn("Sell @%s %f BTC failed" % (kbid, volume))
                result = self.new_order(kask, 'sell', maker_only=False, amount=volume, price=buyprice)
                if not result:
                    logging.warn("2nd sell @%s %f BTC failed" % (kask, volume))
                    return
        else:

            result = self.new_order(kbid, 'sell', maker_only=False, amount= volume,  price=sellprice)
            if not result:
                logging.warn("Sell @%s %f BTC failed" % (kbid, volume))
                return

            self.last_trade = time.time()

            result = self.new_order(kask, 'buy', maker_only=False, amount=volume, price=buyprice)
            if not result:
                logging.warn("Buy @%s %f BTC failed" % (kask, volume))
                result = self.new_order(kbid, 'buy', maker_only=False, amount= volume,  price=sellprice)
                if not result:
                    logging.warn("2nd buy @%s %f BTC failed" % (kbid, volume))
                    return
        return

