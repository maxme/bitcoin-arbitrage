import logging
from .observer import Observer
import json
import time
import os
import math
import os, time
import sys
import traceback
import config

class BasicBot(Observer):
    def __init__(self):
        self.orders = []

        self.max_maker_volume = config.MAKER_MAX_VOLUME
        self.min_maker_volume = config.MAKER_MIN_VOLUME
        self.max_taker_volume = config.TAKER_MAX_VOLUME
        self.min_taker_volume = config.TAKER_MIN_VOLUME

    def new_order(self, kexchange, type, maker_only=True, amount=None, price=None):
        if type == 'buy' or type == 'sell':
            if not price or not amount:
                if type == 'buy':
                    price = self.get_buy_price()
                    amount = math.floor((self.cny_balance/price)*10)/10
                else:
                    price = self.get_sell_price()
                    amount = math.floor(self.btc_balance * 10) / 10
            
            if maker_only:
                amount = min(self.max_maker_volume, amount)
                if amount < self.min_maker_volume:
                    logging.debug('Maker amount is too low %s %s' % (type, amount))
                    return None
            else:
                amount = min(self.max_taker_volume, amount)
                if amount < self.min_taker_volume:
                    logging.debug('Taker amount is too low %s %s' % (type, amount))
                    return None
            
            if maker_only:                
                if type == 'buy':
                    order_id = self.clients[kexchange].buy_maker(amount, price)
                else:
                    order_id = self.clients[kexchange].sell_maker(amount, price)
            else:
                if type == 'buy':
                	order_id = self.clients[kexchange].buy(amount, price)
                else:
                    order_id = self.clients[kexchange].sell(amount, price)

            if not order_id:
                logging.warn("%s @%s %f/%f BTC failed" % (type, kexchange, amount, price))
                return None
            
            print(order_id)
            if order_id == -1:
                logging.warn("%s @%s %f/%f BTC failed, %s" % (type, kexchange, amount, price, order_id))
                return None
            
            order = {
                'market': kexchange, 
                'id': order_id,
                'price': price,
                'amount': amount,
                'deal_amount':0,
                'deal_index': 0, 
                'type': type,
                'maker_only': maker_only,
                'time': time.time()
            }
            self.orders.append(order)
            logging.info("submit order %s" % (order))

            return order

        return None
        

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
            return True

        return False

    def remove_order(self, order_id):
        self.orders = [x for x in self.orders if not x['id'] == order_id]

    def get_orders(self, type):
        orders = [x for x in self.orders if x['type'] == type]
        return orders

    def selling_len(self):
        return len(self.get_orders('sell'))

    def buying_len(self):
        return len(self.get_orders('buy'))

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
        