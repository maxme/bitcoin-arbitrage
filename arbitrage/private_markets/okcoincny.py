# Copyright (C) 2013, Maxime Biais <maxime@biais.org>

from .market import Market, TradeException
import time
import base64
import hmac
import urllib.request
import urllib.parse
import urllib.error
import urllib.request
import urllib.error
import urllib.parse
import hashlib
import sys
import json
import config
from lib.exchange import exchange, market_instance

class PrivateOkCoinCNY(Market):
    haobtc = None
    okcoin = None
    huobi = None

    def __init__(self):
        super().__init__()
        self.haobtc ,self.okcoin, self.huobi = market_instance(exchange)

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
            return False
            raise TradeException(response["error"])

    def get_info(self):
        """Get balance"""
        response = self.okcoin.accountInfo()
        if "error_code" in response:
            raise TradeException(response["error"])
        if response:
            self.btc_balance = float(response['info']['funds']['free']['btc'])
            self.cny_balance = float(response['info']['funds']['free']['cny'])
