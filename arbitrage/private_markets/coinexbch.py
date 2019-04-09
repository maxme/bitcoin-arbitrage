# Copyright (C) 2013, Maxime Biais <maxime@biais.org>

from .marketnofiat import MarketNoFiat, TradeException, GetInfoException
from arbitrage import config
import time
import hashlib
import json as complex_json
import requests

class RequestClient(object):
    __headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36'
    }

    def __init__(self, headers={}):
        self.access_id = config.coinex_api_id
        self.secret_key = config.coinex_api_key
        self.headers = self.__headers
        self.headers.update(headers)

    @staticmethod
    def get_sign(params, secret_key):
        sort_params = sorted(params)
        data = []
        for item in sort_params:
            data.append(item + '=' + str(params[item]))
        str_params = "{0}&secret_key={1}".format('&'.join(data), secret_key)
        token = hashlib.md5(str.encode(str_params)).hexdigest().upper()
        return token

    def set_authorization(self, params):
        params['access_id'] = self.access_id
        params['tonce'] = int(time.time()*1000)
        self.headers['AUTHORIZATION'] = self.get_sign(params, self.secret_key)

    def request(self, method, url, params={}, data='', json={}):
        method = method.upper()
        if method == 'GET':
            self.set_authorization(params)
            result = requests.request('GET', url, params=params, headers=self.headers)
        else:
            if data:
                json.update(complex_json.loads(data))
            self.set_authorization(json)
            result = requests.request(method, url, json=json, headers=self.headers)
        return result




class PrivateCoinexBCH(MarketNoFiat):

    def __init__(self):
        super().__init__()
        self.get_info()        
        

    def _buy(self, amount, price):
        """Create a buy limit order"""
        request_client = RequestClient()

        data = {
                "amount": "%.8f" % (amount*price),
                "price": "%.8f" % (1.0/price),
                "type": "sell",
                "market": "BTCBCH"
            }

        response = request_client.request(
                'POST',
                'https://api.coinex.com/v1/order/limit',
                json=data,
        )

        if response != None:
            data = complex_json.loads(response.text)
            if data["code"] != 0:
                raise TradeException(data["message"])


    def _sell(self, amount, price):
        """Create a sell limit order"""
        request_client = RequestClient()

        data = {
                "amount": "%.8f" % (amount*price),
                "price": "%.8f" % (1.0/price),
                "type": "buy",
                "market": "BTCBCH"
            }

        response = request_client.request(
                'POST',
                'https://api.coinex.com/v1/order/limit',
                json=data,
        )

        if response != None:
            data = complex_json.loads(response.text)
            if data["code"] != 0:
                raise TradeException(data["message"])


    def get_info(self):
        """Get balance"""
        request_client = RequestClient()
        response = request_client.request('GET', 'https://api.coinex.com/v1/balance/')

        if response != None:
            data = complex_json.loads(response.text)
            if data["code"] != 0:
                raise GetInfoException(data["message"])
            elif "data" in data:         
                self.pair1_balance = float(data["data"][str.upper(self.pair1_name)]["available"])
                self.pair2_balance = float(data["data"][str.upper(self.pair2_name)]["available"])
        else:
            raise GetInfoException("Critical error no balances retrieved")



if __name__ == "__main__":
    market = PrivateCoinexBCH()
    market.get_info()
    #market.buy(0.013,0.09)
    #market.sell(0.0035,0.3333)
    print(market)
