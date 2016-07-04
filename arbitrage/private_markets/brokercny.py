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
import logging
import lib.broker_api as exchange_api

class PrivateBrokerCNY(Market):
    def __init__(self):
        super().__init__()

        self.currency = "CNY"
        self.get_info()
        self.client_id = 0

    def _buy(self, amount, price):
        """Create a buy limit order"""
        return
        exchange_api.exchange_buy(self.client_id, amount, price)
 
        self.client_id+=1
    def _sell(self, amount, price):
        """Create a sell limit order"""
        return
        exchange_api.exchange_sell(self.client_id, amount, price)
  
        self.client_id+=1
    def get_info(self):
        """Get balance"""
        accounts = exchange_api.exchange_get_account()
        if accounts:
            self.cny_balance = 0
            self.btc_balance = 0
            self.cny_frozen = 0
            self.btc_frozen = 0

            for account in accounts:
                self.btc_balance += account.available_btc
                self.cny_balance += account.available_cny
                self.btc_frozen +=  account.frozen_cny
                self.cny_frozen +=  account.frozen_btc
