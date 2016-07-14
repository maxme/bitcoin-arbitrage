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
from lib.settings import HAOBTC_API_URL
import logging

class PrivateHaobtcCNY(Market):
    def __init__(self, HAOBTC_API_KEY=None, HAOBTC_SECRET_TOKEN=None):
        super().__init__()
        if HAOBTC_API_KEY == None:
            HAOBTC_API_KEY = config.HAOBTC_API_KEY
            HAOBTC_SECRET_TOKEN = config.HAOBTC_SECRET_TOKEN
        self.market =  exchange(HAOBTC_API_URL, HAOBTC_API_KEY, HAOBTC_SECRET_TOKEN, 'haobtc')

        self.currency = "CNY"
        self.get_info()

    def _buy(self, amount, price):
        """Create a buy limit order"""
        response = self.market.buy(amount, price)
        if response and "code" in response:
            logging.warn (response)
            return False
        if not response:
            return response

        return response['order_id']

    def _sell(self, amount, price):
        """Create a sell limit order"""
        response = self.market.sell(amount, price)
        if response and "code" in response:
            logging.warn (response)
            return False
        if not response:
            return response
        return response['order_id']

    def _buy_maker(self, amount, price):
        response = self.market.bidMakerOnly(amount, price)
        if response and "code" in response:
            logging.warn (response)
            return False
        if not response:
            return response

        return response['order_id']

    def _sell_maker(self, amount, price):
        response = self.market.askMakerOnly(amount, price)
        if response and "code" in response:
            logging.warn (response)
            return False
        if not response:
            return response

        return response['order_id']

    def _get_order(self, order_id):
        response = self.market.orderInfo(order_id)
        if response and "code" in response:
            logging.warn (response)
            return False
        if not response:
            return response
            
        return response

    def _cancel_order(self, order_id):
        response = self.market.cancel(order_id)
        if response and "code" in response:
            logging.warn (response)
            return False
        return response

    def _cancel_all(self):
        response = self.market.cancelAll()
        if response and  "code" in response:
            logging.warn (response)
            return False
        return response

    def get_info(self):
        """Get balance"""
        response = self.market.accountInfo()
        if response:
            if "code" in response:
                logging.warn("get_info failed %s", response)
                return False
            else:
                self.btc_balance = float(response["exchange_btc"])
                self.cny_balance = float(response["exchange_cny"])
                self.btc_frozen = float(response["exchange_frozen_btc"])
                self.cny_frozen = float(response["exchange_frozen_cny"])

        return response
