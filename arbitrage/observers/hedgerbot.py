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
from private_markets import haobtccny, brokercny
from .marketmaker import MarketMaker

class HedgerBot(MarketMaker):
    exchange = 'HaobtcCNY'
    hedger = 'BrokerCNY'
    out_dir = 'hedger_history/'
    filename = exchange + '-bot.csv'

    def __init__(self):
        super().__init__()

        self.clients = {
            "HaobtcCNY": haobtccny.PrivateHaobtcCNY(config.HAOBTC_API_KEY, config.HAOBTC_SECRET_TOKEN),
            "BrokerCNY": brokercny.PrivateBrokerCNY(),
        }

        self.bid_fee_rate = 0.001
        self.ask_fee_rate = 0.001
        self.bid_price_risk = config.bid_price_risk
        self.ask_price_risk = config.ask_price_risk
        self.peer_exchange = self.hedger

        try:
            os.mkdir(self.out_dir)
        except:
            pass

        self.clients[self.exchange].cancel_all()

        logging.info('Setup complete')
        # time.sleep(2)

    def hedge_order(self, order, result):
        if result['deal_size'] <= 0:
            logging.debug("[hedger]NOTHING TO BE DEALED.")
            return

        logging.warn("[hedger]: %s", result)

        order_id = result['order_id']        
        deal_size = result['deal_size']
        price = result['avg_price']

        amount = deal_size - order['deal_amount']
        if amount <= config.broker_min_amount:
            logging.debug("[hedger]deal nothing while.")
            return

        client_id = str(order_id) + '-' + str(order['deal_index'])

        hedge_side = 'SELL' if result['side'] =='BUY' else 'BUY'
        logging.warn('[hedger] %s to broker: %s %s %s', client_id, hedge_side, amount, price)

        if hedge_side == 'SELL':
            self.clients[self.hedger].sell(amount, price, client_id)
        else:
            self.clients[self.hedger].buy(amount, price, client_id)

        # update the deal_amount of local order
        self.remove_order(client_id)
        order['deal_amount'] = deal_size
        order['deal_index'] +=1
        self.orders.append(order)
        
