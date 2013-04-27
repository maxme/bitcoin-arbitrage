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
import config


class PrivateBitcoinCentral(Market):
    balance_url = "https://bitcoin-central.net/api/v1/balances/"
    trade_url = "https://bitcoin-central.net/api/v1/trade_orders/"
    withdraw_url = "https://bitcoin-central.net/api/v1/transfers/send_bitcoins/"

    def __init__(self):
        super().__init__()
        self.username = config.bitcoincentral_username
        self.password = config.bitcoincentral_password
        self.currency = "EUR"
        self.get_info()

    def _create_nonce(self):
        return int(time.time() * 1000000)

    def _send_request(self, url, params=[], extra_headers=None):
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        }
        if extra_headers is not None:
            for k, v in extra_headers.items():
                headers[k] = v

        req = None
        if params:
            req = urllib.request.Request(
                url, json.dumps(params), headers=headers)
        else:
            req = urllib.request.Request(url, headers=headers)
        userpass = '%s:%s' % (self.username, self.password)
        base64string = base64.b64encode(bytes(
            userpass, 'utf-8')).decode('ascii')
        req.add_header("Authorization", "Basic %s" % base64string)
        response = urllib.request.urlopen(req)
        code = response.getcode()
        if code == 200:
            jsonstr = response.read().decode('utf-8')
            return json.loads(jsonstr)
        return None

    def trade(self, amount, ttype, price=None):
        # params = [("amount", amount), ("currency", self.currency), ("type",
        # ttype)]
        params = {"amount": amount, "currency": self.currency, "type": ttype}
        if price:
            params["price"] = price
        response = self._send_request(self.trade_url, params)
        return response

    def buy(self, amount, price=None):
        response = self.trade(amount, "buy", price)

    def sell(self, amount, price=None):
        response = self.trade(amount, "sell", price)
        print(response)

    def withdraw(self, amount, address):
        params = {"amount": amount, "address": address}
        response = self._send_request(self.trade_url, params)
        return response

    def deposit(self):
        return config.bitcoincentral_address

    def get_info(self):
        response = self._send_request(self.balance_url)
        if response:
            self.btc_balance = response["BTC"]
            self.eur_balance = response["EUR"]


if __name__ == "__main__":
    market = PrivateBitcoinCentral()
    market.get_info()
    print(market)
