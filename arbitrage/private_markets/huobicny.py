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
from lib.exchange import exchange
from lib.settings import HUOBI_API_URL

class PrivateHuobiCNY(Market):
    huobi = None

    def __init__(self,HUOBI_API_KEY, HUOBI_SECRET_TOKEN):
        super().__init__()
        self.huobi = exchange(HUOBI_API_URL, HUOBI_API_KEY, HUOBI_SECRET_TOKEN, 'huobi')
        self.currency = "CNY"
        self.get_info()

    def _buy(self, amount, price):
        """Create a buy limit order"""
        response = self.huobi.buy(amount, price)
        if "error" in response:
            raise TradeException(response["error"])

    def _sell(self, amount, price):
        """Create a sell limit order"""
        response = self.huobi.sell(amount, price)
        if "error" in response:
            raise TradeException(response["error"])

    def get_info(self):
        """Get balance"""
        response = self.huobi.accountInfo()
        if "error" in response:
            raise TradeException(response["error"])
        if response:
            self.btc_balance = float(response["available_btc_display"])
            self.cny_balance = float(response["available_cny_display"])
