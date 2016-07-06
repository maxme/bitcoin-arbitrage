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
        self.bid_price_risk = 1
        self.ask_price_risk = 1
        self.peer_exchange = self.hedger

        try:
            os.mkdir(self.out_dir)
        except:
            pass

        self.clients[self.exchange].cancel_all()

        logging.info('Setup complete')
        # time.sleep(2)

    def hedge_order(self, order):
        if order['deal_size'] <= 0:
            logging.debug("[hedger]NOTHING TO BE DEALED.")
            return

        logging.warn("[hedger]: %s", order)

        client_id = order['order_id']
        amount = order['deal_size']
        price = order['avg_price']

        hedge_side = 'SELL' if order['side'] =='BUY' else 'BUY'
        logging.warn('[hedger] %s to broker: %s %s %s', client_id, hedge_side, amount, price)

        if hedge_side == 'SELL':
            self.clients[self.hedger].sell(amount, price, client_id)
        else:
            self.clients[self.hedger].buy(amount, price, client_id)


        
