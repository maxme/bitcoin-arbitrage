import logging
from .observer import Observer
import json
import time
import os
from private_markets import bitstampusd,haobtccny,huobicny,okcoincny
import math
import os, time
import sys
import traceback
import config

class MarketMaker(Observer):
    exchange = 'HaobtcCNY'
    out_dir = 'trade_history/'
    try:
        filename = exchange + config.ENV+ '.csv'
    except Exception as e:
        filename = exchange + '.csv'


    def __init__(self):
        self.clients = {
            # TODO: move that to the config file
            "HaobtcCNY": haobtccny.PrivateHaobtcCNY(config.HAOBTC_API_KEY, config.HAOBTC_SECRET_TOKEN),
        }
        
        self.trade_timeout = 10  # in seconds

        self.orders = []

        self.cny_balance = 0
        self.btc_balance = 0
        self.cny_total = 0
        self.btc_total = 0

        self.max_tx_volume = config.MAKER_MAX_VOLUME
        self.min_tx_volume = config.MAKER_MIN_VOLUME
        self.bid_fee_rate = 0.0005
        self.ask_fee_rate = 0.001
        self.bid_price_risk = 0
        self.ask_price_risk = 0

        self.peer_exchange ='OKCoinCNY'
        # self.peer_exchange ='HuobiCNY'

        try:
            os.mkdir(self.out_dir)
        except:
            pass

        for kclient in self.clients:
            self.clients[kclient].cancel_all()

        logging.info('Setup complete')
        # time.sleep(2)

    def hedge_order(self, order):
        pass

    def market_maker(self, depths):
        kexchange = self.exchange

        # update price
        try:
            bid_price = int(depths[self.exchange]["bids"][0]['price'])
            ask_price =  int(depths[self.exchange]["asks"][0]['price'])
            bid1_price = int(depths[self.exchange]["bids"][1]['price'])
            ask1_price =  int(depths[self.exchange]["asks"][1]['price'])
            peer_bid_price = int(depths[self.peer_exchange]["bids"][0]['price'])
            peer_ask_price = int(depths[self.peer_exchange]["asks"][0]['price'])
            bid_amount = (depths[self.exchange]["bids"][0]['amount'])
            ask_amount=  (depths[self.exchange]["asks"][0]['amount'])
        except  Exception as ex:
            logging.warn("exception depths:%s" % ex)
            traceback.print_exc()
            return

        if bid_price == 0 or ask_price == 0 or peer_bid_price == 0 or peer_bid_price == 0:
            logging.warn("exception ticker")
            return

        if bid_price+1 < ask_price :
            buyprice = bid_price + 1
        else:
            buyprice = bid_price

        if ask_price-1 > bid_price:
            sellprice = ask_price - 1
        else:
            sellprice = ask_price

        if buyprice == sellprice:
            if buyprice > bid_price:
                buyprice -=1
            elif sellprice < ask_price:
                sellprice +=1

        peer_bid_hedge_price = int(peer_bid_price*(1+self.bid_fee_rate))
        peer_ask_hedge_price = int(peer_ask_price*(1-self.ask_fee_rate))

        buyprice=min(buyprice, peer_bid_hedge_price) - self.bid_price_risk
        sellprice=max(sellprice, peer_ask_hedge_price) + self.ask_price_risk
        logging.info("sellprice/buyprice=(%s/%s)" % (sellprice, buyprice))

        self.buyprice = buyprice
        self.sellprice = sellprice

        # Update client balance
        self.update_balance()

        # query orders
        if self.is_buying():
            for buy_order in self.get_orders('buy'):
                logging.info(buy_order)
                result = self.clients[kexchange].get_order(buy_order['id'])
                logging.info (result)
                if not result:
                    logging.warn("get_order buy #%s failed" % (buy_order['id']))
                    return

                if result['status'] == 'CLOSE' or result['status'] == 'CANCELED':
                    self.remove_order(buy_order['id'])
                    self.hedge_order(result)
                else:
                    current_time = time.time()
                    if (result['price'] != buyprice) and \
                        ((result['price'] > peer_bid_hedge_price) or \
                        ( current_time - buy_order['time'] > self.trade_timeout and  \
                        (result['price'] < bid_price or result['price'] > (bid1_price + 1)))):
                        logging.info("[TraderBot] cancel last buy trade " +
                                     "occured %.2f seconds ago" %
                                     (current_time - buy_order['time']))
                        logging.info("buyprice %s result['price'] = %s[%s]" % (buyprice, result['price'], result['price'] != buyprice))

                        self.cancel_order(kexchange, 'buy', buy_order['id'])


        if self.is_selling():
            for sell_order in self.get_orders('sell'):
                logging.info(sell_order)
                result = self.clients[kexchange].get_order(sell_order['id'])
                logging.info (result)
                if not result:
                    logging.warn("get_order sell #%s failed" % (sell_order['id']))
                    return

                if result['status'] == 'CLOSE' or result['status'] == 'CANCELED':
                    self.remove_order(sell_order['id'])
                    self.hedge_order(result)
                else:
                    current_time = time.time()
                    if (result['price'] != sellprice) and \
                        ((result['price'] < peer_ask_hedge_price) or \
                        (current_time - sell_order['time'] > self.trade_timeout and \
                            (result['price'] > ask_price or result['price'] < (ask1_price - 1)))):
                        logging.info("[TraderBot] cancel last SELL trade " +
                                     "occured %.2f seconds ago" %
                                     (current_time - sell_order['time']))
                        logging.info("sellprice %s result['price'] = %s [%s]" % (sellprice, result['price'], result['price'] != sellprice))

                        self.cancel_order(kexchange, 'sell', sell_order['id'])

        # excute trade
        if not self.is_buying():
            self.new_order(kexchange, 'buy')
        if not self.is_selling():
            self.new_order(kexchange, 'sell')

    def update_trade_history(self, time, price, cny, btc):
        filename = self.out_dir + self.filename
        need_header = False

        if not os.path.exists(filename):
            need_header = True

        fp = open(filename, 'a+')

        if need_header:
            fp.write("timestamp, price, cny, btc\n")

        fp.write(("%d") % time +','+("%.2f") % price+','+("%.2f") % cny+','+ str(("%.4f") % btc) +'\n')
        fp.close()

    def new_order(self, kexchange, type):
        if type == 'buy' or type == 'sell':
            if type == 'buy':
                price = self.get_buy_price()
                amount = math.floor((self.cny_balance/price)*10)/10
            else:
                price = self.get_sell_price()
                amount = math.floor(self.btc_balance * 10) / 10
            
            amount = min(self.max_tx_volume, amount)
            if amount < self.min_tx_volume:
                logging.debug('Amount is too low %s %s' % (type, amount))
                return False
            else:
                if type == 'buy':
                    result = self.clients[kexchange].buy_maker(amount, price)
                else:
                    result = self.clients[kexchange].sell_maker(amount, price)

            if result == False:
                logging.warn("%s @%s %f/%f BTC failed" % (type, kexchange, amount, price))
            else:
                order_id = result['order_id']
                if order_id == -1:
                    logging.warn("%s @%s %f/%f BTC failed, %s" % (type, kexchange, amount, price, order_id))
                else:
                    order = {
                        'market': kexchange, 
                        'id': order_id,
                        'price': price,
                        'amount': amount,
                        'type': type,
                        'time': time.time()
                    }
                    self.orders.append(order)
                    logging.info("submit order %s" % (order))

                    return True
        return False
        

    def cancel_order(self, kexchange, type, order_id):
        result = self.clients[kexchange].cancel_order(order_id)
        if not result:
            logging.warn("cancel %s #%s failed" % (type, order_id))
            return

        resp_order_id = result['order_id']
        if resp_order_id == -1:
            logging.warn("cancel %s #%s failed, %s" % (type, order_id, resp_order_id))
        else:
            logging.info("Canceled order %s #%s ok" % (type, order_id))
            # self.remove_order(order_id)
            return True

        return False

    def remove_order(self, order_id):
        self.orders = [x for x in self.orders if not x['id'] == order_id]

    def get_orders(self, type):
        orders = [x for x in self.orders if x['type'] == type]
        return orders

    def is_selling(self):
        return len(self.get_orders('sell')) > 0

    def is_buying(self):
        return len(self.get_orders('buy')) > 0

    def get_sell_price(self):
        return self.sellprice

    def get_buy_price(self):
        return self.buyprice

    def get_spread(self):
        return self.sellprice - self.buyprice

    def update_price(self):
        pass

    def update_balance(self):
        for kclient in self.clients:
            if kclient == self.exchange:
                self.clients[kclient].get_info()
                self.cny_balance = self.clients[kclient].cny_balance
                self.btc_balance = self.clients[kclient].btc_balance
                
                self.cny_frozen = self.clients[kclient].cny_frozen
                self.btc_frozen = self.clients[kclient].btc_frozen

        cny_abs = abs(self.cny_total - self.cny_balance_total(self.buyprice))
        cny_diff = self.cny_total*0.1
        btc_abs = abs(self.btc_total - self.btc_balance_total(self.sellprice))
        btc_diff = self.btc_total*0.1

        self.cny_total = self.cny_balance_total(self.buyprice)
        self.btc_total = self.btc_balance_total(self.sellprice)

        if (cny_abs > 5 and cny_abs < cny_diff) or (btc_abs > 0.001 and btc_abs < btc_diff):
            logging.debug("update_balance-->")
            self.update_trade_history(time.time(), self.buyprice, self.cny_total, self.btc_total)

        logging.info("cny_balance=%s/%s, btc_balance=%s/%s, total_cny=%0.2f, total_btc=%0.2f", 
            self.cny_balance, self.cny_frozen, self.btc_balance, self.btc_frozen, 
            self.cny_balance_total(self.buyprice), self.btc_balance_total(self.sellprice))

    def cny_balance_total(self, price):
        return self.cny_balance + self.cny_frozen+ (self.btc_balance + self.btc_frozen)* price
    
    def btc_balance_total(self, price):
        return self.btc_balance + self.btc_frozen  + (self.cny_balance +self.cny_frozen ) / (price*1.0)

    def begin_opportunity_finder(self, depths):
        self.market_maker(depths)

    def end_opportunity_finder(self):
        pass

    def opportunity(self, profit, volume, buyprice, kask, sellprice, kbid, perc, weighted_buyprice, weighted_sellprice):
        pass
