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
    okcoin = None

    def __init__(self,OKCOIN_API_KEY = None, OKCOIN_SECRET_TOKEN = None):
        super().__init__()
        if OKCOIN_API_KEY == None:
            OKCOIN_API_KEY = config.OKCOIN_API_KEY
            OKCOIN_SECRET_TOKEN = config.OKCOIN_SECRET_TOKEN
        self.okcoin = exchange(OKCOIN_API_URL, OKCOIN_API_KEY, OKCOIN_SECRET_TOKEN, 'okcoin')

        self.currency = "CNY"
        self.get_info()

    def _buy(self, amount, price):
        """Create a buy limit order"""
        response = self.okcoin.buy(amount, price)
        if "error_code" in response:
            print(response)
            return False
            raise TradeException(response["error"])

    def _sell(self, amount, price):
        """Create a sell limit order"""
        response = self.okcoin.sell(amount, price)
        if "error_code" in response:
            print(response)
            return False
            raise TradeException(response["error"])

    def get_info(self):
        """Get balance"""
        response = self.okcoin.accountInfo()
        if "error_code" in response:
            print(response)
            return False
            raise TradeException(response["error"])
        if response:
            self.btc_balance = float(response['info']['funds']['free']['btc'])
            self.cny_balance = float(response['info']['funds']['free']['cny'])
            self.btc_frozen =  float(response['info']['funds']['freezed']['btc'])
            self.cny_frozen =  float(response['info']['funds']['freezed']['cny'])
