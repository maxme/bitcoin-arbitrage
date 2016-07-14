# Copyright (C) 2016, Philsong <songbohr@gmail.com>

from .market import Market, TradeException
import time
import base64
import hmac
import urllib.request
import urllib.parse
import urllib.error
import hashlib
import sys
import json
import config
from lib.exchange import exchange
from lib.settings import OKCOIN_API_URL
import logging

class PrivateOkCoinCNY(Market):
    def __init__(self,OKCOIN_API_KEY = None, OKCOIN_SECRET_TOKEN = None):
        super().__init__()
        if OKCOIN_API_KEY == None:
            OKCOIN_API_KEY = config.OKCOIN_API_KEY
            OKCOIN_SECRET_TOKEN = config.OKCOIN_SECRET_TOKEN
        self.market = exchange(OKCOIN_API_URL, OKCOIN_API_KEY, OKCOIN_SECRET_TOKEN, 'okcoin')

        self.currency = "CNY"
        self.get_info()

    def _buy(self, amount, price):
        """Create a buy limit order"""
        response = self.market.buy(amount, price)
        if response and "error_code" in response:
            logging.warn(response)
            return False
        if not response:
            return response

        return response['order_id']

    def _sell(self, amount, price):
        """Create a sell limit order"""
        response = self.market.sell(amount, price)
        if response and "error_code" in response:
            logging.warn(response)
            return False

        if not response:
            return response

        return response['order_id']

    def _get_order(self, order_id):
        response = self.market.orderInfo(order_id)

        if response and "error_code" in response:
            logging.warn (response)
            return False
        if not response:
            return response

        order = response['orders'][0]
        resp = {}
        resp['order_id'] = order['order_id']
        resp['amount'] = order['amount']
        resp['price'] = order['price']
        resp['deal_size'] = order['deal_amount']
        resp['avg_price'] = order['avg_price']

        status = order['status']
        if status == -1:
            resp['status'] = 'CANCELED'
        elif status == 2:
            resp['status'] = 'CLOSE'
        else:
            resp['status'] = 'OPEN'
        return resp

    def _cancel_order(self, order_id):
        response = self.market.cancel(order_id)
        if response and "error_code" in response:
            logging.warn (response)
            return False
        if not response:
            return response
            
        return response

    def get_info(self):
        """Get balance"""
        response = self.market.accountInfo()
        if response:
            if "error_code" in response:
                logging.warn(response)
                return False
            else:
                self.btc_balance = float(response['info']['funds']['free']['btc'])
                self.cny_balance = float(response['info']['funds']['free']['cny'])
                self.btc_frozen =  float(response['info']['funds']['freezed']['btc'])
                self.cny_frozen =  float(response['info']['funds']['freezed']['cny'])
        return response
        