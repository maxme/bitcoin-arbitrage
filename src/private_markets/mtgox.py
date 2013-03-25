from market import Market
import time
import base64
import hmac
import urllib
import urllib2
import hashlib
import json
import re
from decimal import Decimal
import config
import logging


class PrivateMtGox(Market):

    ticker_url = {"method": "GET", "path":
                  "BTCUSD/public/ticker"}
    buy_url = {"method": "POST", "path":
               "BTCUSD/private/order/add"}
    sell_url = {"method": "POST", "path":
                "BTCUSD/private/order/add"}
    order_url = {"method": "POST", "path":
                 "generic/private/order/result"}
    open_orders_url = {"method": "POST", "path":
                       "generic/private/orders"}
    info_url = {"method": "POST", "path":
                "generic/private/info"}
    withdraw_url = {"method": "POST", "path":
                    "generic/bitcoin/send_simple"}
    deposit_url = {"method": "POST", "path":
                   "generic/bitcoin/address"}

    def __init__(self):
        super(Market, self).__init__()
        self.key = config.mtgox_key
        self.secret = config.mtgox_secret
        self.currency = "EUR"
        self.get_info()

    def _change_currency_url(self, url, currency):
        return re.sub(r'BTC\w{3}', r'BTC' + currency, url)

    def _to_int_price(self, price, currency):
        ret_price = None
        if currency in ["USD", "EUR", "GBP", "PLN", "CAD", "AUD", "CHF", "CNY",
                        "NZD", "RUB", "DKK", "HKD", "SGD", "THB"]:
            ret_price = Decimal(price)
            ret_price = int(price * 100000)
        elif currency in ["JPY", "SEK"]:
            ret_price = Decimal(price)
            ret_price = int(price * 1000)
        return ret_price

    def _to_int_amount(self, amount):
        amount = Decimal(amount)
        return int(amount * 100000000)

    def _from_int_amount(self, amount):
        return Decimal(amount) / Decimal(100000000.)

    def _from_int_price(self, amount):
        # FIXME: should take JPY and SEK into account
        return Decimal(amount) / Decimal(100000.)

    def _send_request(self, path, params=[], extra_headers=None):
        # API 2 Seems not yet ready
        # url = 'https://mtgox.com/api/2/' + path['path']
        url = 'https://mtgox.com/api/1/' + path['path']
        params += [(u'nonce', str(int(time.time() * 1000)))]
        post_data = urllib.urlencode(params)

        # API 2 Seems not yet ready
        # api2postdatatohash = path['path'] + chr(0) + post_data
        # ahmac = base64.b64encode(str(hmac.new(base64.b64decode(
        #    self.secret), api2postdatatohash, hashlib.sha512).digest()))
        ahmac = base64.b64encode(str(hmac.new(base64.b64decode(self.secret),
                                 post_data, hashlib.sha512).digest()))

        headers = {
            'Rest-Key': self.key,
            'Rest-Sign': ahmac,
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        }
        if extra_headers is not None:
            for k, v in extra_headers.iteritems():
                headers[k] = v

        try:
            req = urllib2.Request(url, post_data, headers)
            response = urllib2.urlopen(req)
            if response.getcode() == 200:
                jsonstr = response.read()
            return json.loads(jsonstr)
        except Exception, err:
            logging.error('Can t request MTGox, %s' % err)
            return None
        return None

    def trade(self, amount, ttype, price=None):
        if price:
            price = self._to_int_price(price, self.currency)
        amount = self._to_int_amount(amount)

        self.buy_url["path"] = self._change_currency_url(self.buy_url["path"],
                                                         self.currency)

        params = [("amount_int", str(amount)),
                  ("type", ttype)]
        if price:
            params.append(("price_int", str(price)))

        response = self._send_request(self.buy_url, params)
        if response and "result" in response \
                and response["result"] == "success":
            return response["return"]
        return None

    def buy(self, amount, price=None):
        return self.trade(amount, "bid", price)

    def sell(self, amount, price=None):
        return self.trade(amount, "ask", price)

    def withdraw(self, amount, address):
        params = [("amount_int", str(self._to_int_amount(amount))),
                  ("address", address)]
        response = self._send_request(self.withdraw_url, params)
        if response and "result" in response \
                and response["result"] == "success":
            return response["return"]
        return None

    def deposit(self, ):
        params = []
        response = self._send_request(self.deposit_url, params)
        if response and "result" in response \
                and response["result"] == "success":
            return response["return"]
        return None

    def get_info(self):
        params = []
        response = self._send_request(self.info_url, params)
        if response and "result" in response \
                and response["result"] == "success":
            self.btc_balance = self._from_int_amount(int(
                response["return"]["Wallets"]["BTC"]["Balance"]["value_int"]))
            self.eur_balance = self._from_int_price(int(
                response["return"]["Wallets"]["EUR"]["Balance"]["value_int"]))
            return 1
        return None

    def __str__(self):
        return str({"btc_balance": self.btc_balance, "eur_balance": self.eur_balance})


if __name__ == "__main__":
    mtgox = PrivateMtGox()
    mtgox.get_info()
    print mtgox
    print mtgox.deposit()
