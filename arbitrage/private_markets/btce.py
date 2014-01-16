# Copyright (C) 2013, Maxime Biais <maxime@biais.org>

from .market import Market, TradeException
import time
import base64
import hmac
import urllib.parse
import http.client
import hashlib
import sys
import json
import config
import random
import logging

class FileKV(object):
    def set(self, key, value):
        with open(key, 'w') as f:
            f.write(value)

    def get(self, key, default = None):
        try:
            with open(key, 'r') as f:
                result = f.read()
        except OSError:
            result = default

        return result

class PrivateBtce(Market):

    def __init__(self, kv_store=FileKV()):
        super().__init__()
        self.api_key = config.btce_api_key
        self.api_secret = config.btce_api_secret
        self.kv = kv_store
        self.nonce = self._get_nonce()
        self.get_info()

    def _get_nonce(self):
        return int(self.kv.get("%s.nonce" % self.api_key, default = 0))

    def _send_request(self, params, extra_headers=None):
        self.nonce += 1
        params.update({
            "nonce": self.nonce
        })
        params = urllib.parse.urlencode(params)

        hash = hmac.new(
            bytes(self.api_secret, 'utf-8'), digestmod=hashlib.sha512
        )
        hash.update(bytes(params, 'utf-8'))

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
        self.kv.set("%s.nonce" % self.api_key, str(self.nonce))

        if response.status == 200:
            return json.loads(response.readall().decode('utf-8'))
        return None

    def execute(self, trade):
        logging.debug("[BTC-e] Got command \"%s\"" % str(trade))
        pair = "%s_%s" % (
            trade.amount_currency.lower(), trade.price_currency.lower()
        )
        response = self._try_execute(trade, pair)

        if response["success"] == 0 \
        and response["error"] == 'invalid parameter: pair':
            pair = "%s_%s" % (
                trade.price_currency.lower(), trade.amount_currency.lower()
            )
            response = self._try_execute(trade, pair)

        return response

    def _try_execute(self, trade, pair): 
        return self._send_request({
            "method": "Trade",
            "type": trade.type,
            "rate": trade.price,
            "amount": trade.amount,
            "pair": pair
        })

    def get_info(self):
        """Get balance"""
        response = self._send_request({
            "method": "getInfo"
        })

        if response and "return" in response and "funds" in response["return"]:
            for currency, balance in response["return"]["funds"].items():
                self.balances[currency.upper()] = float(balance)
