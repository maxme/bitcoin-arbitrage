# Copyright (C) 2013, Maxime Biais <maxime@biais.org>

from .market import Market, TradeException, GetInfoException
from arbitrage import config
import time
import base64
import hmac
import urllib.request
import urllib.parse
import urllib.error
import hashlib
import sys
import json
import requests

class PrivateBitstampUSD(Market):
    balance_url = "https://www.bitstamp.net/api/balance/"
    buy_url = "https://www.bitstamp.net/api/buy/"
    sell_url = "https://www.bitstamp.net/api/sell/"

    def __init__(self):
        super().__init__()
        self.proxydict = None
        self.client_id = config.bitstamp_client_id
        self.api_key = config.bitstamp_api_key
        self.api_secret = config.bitstamp_api_secret
        self.currency = "USD"
        self.get_info()        
        
    def _create_nonce(self):
        return int(time.time() * 1000000)

    def _send_request(self, url, params={}, extra_headers=None):
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        }
        if extra_headers is not None:
            for k, v in extra_headers.items():
                headers[k] = v
        nonce = str(self._create_nonce())
        message = nonce + self.client_id + self.api_key
        if sys.version_info.major == 2:
            signature = hmac.new(self.api_secret, msg=message, digestmod=hashlib.sha256).hexdigest().upper()
        else:
            signature = hmac.new(str.encode(self.api_secret), msg=str.encode(message), digestmod=hashlib.sha256).hexdigest().upper()
        params['key'] = self.api_key
        params['signature'] = signature
        params['nonce'] = nonce
        #postdata = urllib.parse.urlencode(params).encode("utf-8")
        #req = urllib.request.Request(url, postdata, headers=headers)
        #print ("req=", postdata)
        #response = urllib.request.urlopen(req)
        response = requests.post(url, data=params, proxies=self.proxydict)
        #code = response.getcode()
        code = response.status_code
        if code == 200:
            #jsonstr = response.read().decode('utf-8')
            #return json.loads(jsonstr)
            if 'error' in response.json():
                return False, response.json()['error']
            else:
                return response.json()
        return None

    def _buy(self, amount, price):
        """Create a buy limit order"""
        params = {"amount": amount, "price": price}
        response = self._send_request(self.buy_url, params)
        if "error" in response:
            raise TradeException(response["error"])

    def _sell(self, amount, price):
        """Create a sell limit order"""
        params = {"amount": amount, "price": price}
        response = self._send_request(self.sell_url, params)
        if "error" in response:
            raise TradeException(response["error"])

    def get_info(self):
        """Get balance"""
        response = self._send_request(self.balance_url)
        if False in response:
            raise GetInfoException(response[1])
        if response:
            #print(json.dumps(response))            
            self.btc_balance = float(response["btc_available"])
            self.usd_balance = float(response["usd_available"])
            self.pair1_balance = float(response[str.lower(self.pair1_name)+"_balance"])
            self.pair2_balance = float(response[str.lower(self.pair2_name)+"_balance"])
        else:
            raise GetInfoException("Critical error no balances retrieved")