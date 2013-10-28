# Copyright (C) 2013, Maxime Biais <maxime@biais.org>

from .market import Market, TradeException
import time
import base64
import hmac
import urllib.urlencode
import http.client
import hashlib
import sys
import json
import config
import random
import logging

class PrivateBtce(Market):

    def __init__(self):
        super().__init__()
        self.api_key = config.btce_api_key
        self.api_secret = config.btce_api_secret
        self.get_info()

    def _send_request(self, params, extra_headers=None):
        params.update({
            "nonce": random.SystemRandom().randint(sys.maxsize*-1, sys.maxsize)
        })
        params = urllib.urlencode(params)

        hash = hmac.new(self.api_secret, digestmod=hashlib.sha512)
        hash.update(params)

        headers = {
            'Content-type': 'application/x-www-form-urlencoded',
            'Key': self.api_key,
            'Sign': hash.hexdigest()
        }

        if extra_headers is not None:
            for k, v in extra_headers.items():
                headers[k] = v

        conn = http.client.HTTPSConnection("btc-e.com")
        conn.request("POST", "/tapi", params, headers)
        response = conn.getresponse()

        if reponse.status == 200:
            return json.load(response)
        return None

    def execute(self, trade):
        logging.debug("[BTC-e] Got command \"%s\"" % str(trade))
        return self._send_request({
            "method": "Trade",
            "type": trade.type,
            "rate": trade.price,
            "amount": trade.amount,
            "pair": "%s_%s" % (trade.amount_currency, trade.price_currency)
        })

    def get_info(self):
        """Get balance"""
        response = self._send_request({
            "method": "getInfo"
        })
        if response and "return" in response and "funds" in response["return"]:
            for currency, balance in response["return"]["funds"]:
                self.balances[currency.upper()] = float(balance)
