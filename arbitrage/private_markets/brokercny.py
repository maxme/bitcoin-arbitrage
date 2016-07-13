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
        exchange_api.init_broker()

        self.filename = "broker-clientid.json"
        try:
            self.load()
        except IOError:
            logging.warn("load client id failed!")
            pass

    def load(self):
        data = json.load(open(self.filename, "r"))
        self.client_id = data["client_id"]

    def save(self):
        data = {'client_id': self.client_id}
        json.dump(data, open(self.filename, "w"))

    def _buy(self, amount, price, client_id=None):
        """Create a buy limit order"""
        if not client_id:
            self.client_id+=1
            client_id = self.client_id
            self.save()
        
        exchange_api.exchange_buy(client_id, amount, price)
 
    def _sell(self, amount, price, client_id=None):
        """Create a sell limit order"""
        if not client_id:
            self.client_id+=1
            client_id = self.client_id
            self.save()
        
        exchange_api.exchange_sell(client_id, amount, price)

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
