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
from lib.exchange import exchange
from lib.settings import HUOBI_API_URL
import sys
import traceback
import config
import logging

class PrivateHuobiCNY(Market):
    huobi = None

    def __init__(self,HUOBI_API_KEY=None, HUOBI_SECRET_TOKEN=None):
        super().__init__()
        if HUOBI_API_KEY == None:
            HUOBI_API_KEY = config.HUOBI_API_KEY
            HUOBI_SECRET_TOKEN = config.HUOBI_SECRET_TOKEN
        self.huobi = exchange(HUOBI_API_URL, HUOBI_API_KEY, HUOBI_SECRET_TOKEN, 'huobi')
        self.currency = "CNY"
        self.get_info()

    def _buy(self, amount, price):
        """Create a buy limit order"""
        response = self.huobi.buy(amount, price)
        if "code" in response:
            print(response)
            return False
            raise TradeException(response["message"])

    def _sell(self, amount, price):
        """Create a sell limit order"""
        response = self.huobi.sell(amount, price)
        if "code" in response:
            print(response)
            return False
            raise TradeException(response["message"])

    def get_info(self):
        """Get balance"""
        try:
            response = self.huobi.accountInfo()
            if "code" in response:
                print(response)
                return False
                raise TradeException(response["message"])
            if response:
                self.btc_balance = float(response["available_btc_display"])
                self.cny_balance = float(response["available_cny_display"])
                self.btc_frozen = float(response["frozen_btc_display"])
                self.cny_frozen = float(response["frozen_cny_display"])
        except  Exception as ex:
            logging.warn("get_info failed :%s" % ex)
            t,v,tb = sys.exc_info()
            traceback.print_exc()

            return False

