# Copyright (C) 2013, Maxime Biais <maxime@biais.org>

from .market import Market
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


class PrivateMtGox(Market):
    def __init__(self):
        super().__init__()
        self.order_url = {"method": "POST", "url":
                          "https://mtgox.com/api/1/generic/private/order/result"}
        self.open_orders_url = {"method": "POST", "url":
                                "https://mtgox.com/api/1/generic/private/orders"}
        self.info_url = {"method": "POST", "url":
                         "https://mtgox.com/api/1/generic/private/info"}
        self.withdraw_url = {"method": "POST", "url":
                        "https://mtgox.com/api/1/generic/bitcoin/send_simple"}
        self.deposit_url = {"method": "POST", "url":
                            "https://mtgox.com/api/1/generic/bitcoin/address"}

        self.key = config.mtgox_key
        self.secret = config.mtgox_secret
        self.get_info()

    def _create_nonce(self):
        return int(time.time() * 1000000)

    def _to_int_price(self, price, currency):
        ret_price = None
        if currency in ["USD", "EUR", "GBP", "PLN", "CAD", "AUD", "CHF", "CNY",
                        "NZD", "RUB", "DKK", "HKD", "SGD", "THB"]:
            ret_price = price
            ret_price = int(price * 100000)
        elif currency in ["JPY", "SEK"]:
            ret_price = price
            ret_price = int(price * 1000)
        return ret_price

    def _to_int_amount(self, amount):
        amount = amount
        return int(amount * 100000000)

    def _from_int_amount(self, amount):
        return amount / 100000000.

    def _from_int_price(self, amount):
        # FIXME: should take JPY and SEK into account
        return amount / 100000.

    def _get_trade_url(self, trade):
        return {"method": "POST",
            "url": "https://mtgox.com/api/1/%s%s/private/order/add" % (
                trade.amount_currency, trade.price_currency
            )
        }

    def _send_request(self, url, params, extra_headers=None):
        urlparams = bytes(urllib.parse.urlencode(params), "UTF-8")
        secret_from_b64 = base64.b64decode(bytes(self.secret, "UTF-8"))
        hmac_secret = hmac.new(secret_from_b64, urlparams, hashlib.sha512)

        headers = {
            'Rest-Key': self.key,
            'Rest-Sign': base64.b64encode(hmac_secret.digest()),
            'Content-type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        }
        if extra_headers is not None:
            for k, v in extra_headers.items():
                headers[k] = v
        try:
            req = urllib.request.Request(url['url'],
                                         bytes(urllib.parse.urlencode(params),
                                               "UTF-8"), headers)
            response = urllib.request.urlopen(req)
            if response.getcode() == 200:
                jsonstr = response.read()
                return json.loads(str(jsonstr, "UTF-8"))
        except Exception as err:
            logging.error('Can\'t request MTGox, %s' % err)
        return None

    def execute(self, trade):
        logging.debug("[MtGox] Got command \"%s\"" % str(trade))
        price = self._to_int_price(trade.price, trade.price_currency)
        amount = self._to_int_amount(trade.amount)
        trade_url = self._get_trade_url(trade)

        params = [("nonce", self._create_nonce()),
                  ("amount_int", str(amount)),
                  ("type", trade.type),
                  ("price_int", str(price))
        ]

        response = self._send_request(trade_url, params)
        if response and "result" in response \
        and response["result"] == "success":
            return response["return"]
        return None

    def withdraw(self, amount, address):
        params = [("nonce", self._create_nonce()),
                  ("amount_int", str(self._to_int_amount(amount))),
                  ("address", address)]
        response = self._send_request(self.withdraw_url, params)
        if response and "result" in response and \
           response["result"] == "success":
            return response["return"]
        return None

    def deposit(self):
        params = [("nonce", self._create_nonce())]
        response = self._send_request(self.deposit_url, params)
        if response and "result" in response and \
           response["result"] == "success":
            return response["return"]
        return None

    def get_info(self):
        params = [("nonce", self._create_nonce())]
        response = self._send_request(self.info_url, params)
        if response and "result" in response and response["result"] == "success":
            for currency, wallet in response["return"]["Wallets"]:
                self.balances[currency] = self._from_int_amount(int(
                    wallet["Balance"]["value_int"]
                ))
            return 1
        return None
