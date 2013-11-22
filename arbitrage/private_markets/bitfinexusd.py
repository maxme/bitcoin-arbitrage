from .market import Market
from decimal import Decimal
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
import re
import logging
import config


class PrivateBitfinexUSD(Market):
    def __init__(self):
        super().__init__()
        self.order_url = "https://api.bitfinex.com/v1/order/new"
        self.balance_url = "https://api.bitfinex.com/v1/balances"
        self.key = config.bitfinex_apikey
        self.secret = config.bitfinex_apisecret
        self.currency = "USD"
        self.get_info()

    def _prepare_payload(self, should_sign, d):
        j = json.dumps(d)
        data = base64.standard_b64encode(j.encode('ascii'))

        if should_sign:
            h = hmac.new(self.secret.encode('ascii'), data, hashlib.sha384)
            signature = h.hexdigest()

            return {
                "X-BFX-APIKEY": self.key,
                "X-BFX-SIGNATURE": signature,
                "X-BFX-PAYLOAD": data,
            }
        else:
            return {
                "X-BFX-PAYLOAD": data,
            }

    def trade(self, amount, side, price):
        payload = {}
        payload["request"] = "/v1/order/new"
        payload["nonce"] = str(long(time.time() * 100000))
        headers = self._prepare_payload(True, payload)
        params = [("symbol", "btcusd"),
                  ("amount", float(amount)),  # Decimal would be better but sometimes has issues with the JSON module...
                  ("price", float(price)),
                  ("exchange", "bitfinex"),  # only BFX internal!
                  ("side", side),
                  ("type", "exchange limit")]  # NOT "limit" - that's on margin!
        req = urllib.request.Request(
            self.order_url,
            params,
            headers)
        res = urllib.request.urlopen(req)
        # TODO: return None on error
        # TODO: make sure that the transaction actually took place
        answer = json.loads(res.read().decode('utf8'))
        print(answer)
        return "success"

    def _buy(self, amount, price):
        return self.trade(amount, "buy", price)

    def _sell(self, amount, price):
        return self.trade(amount, "sell", price)

    def withdraw(self, amount, address):
        # TODO: implement
        return None

    def deposit(self):
        # TODO: implement
        return None

    def get_info(self):
        payload = {}
        payload["request"] = "/v1/balances"
        payload["nonce"] = str(int(time.time() * 100000))
        headers = self._prepare_payload(True, payload)
        req = urllib.request.Request(
            self.balance_url,
            None,
            headers)
        res = urllib.request.urlopen(req)
        # TODO: return None on error
        answer = json.loads(res.read().decode('utf8'))
        for balance in answer:
            if balance['type'] == "exchange":
                if balance['currency'] == "btc":
                    self.btc_balance = float(balance['available'])  # or 'amount'?
                elif balance['currency'] == "usd":
                    self.usd_balance = float(balance['available'])
        return 1