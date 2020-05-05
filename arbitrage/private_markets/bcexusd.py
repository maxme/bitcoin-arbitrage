# Copyright (C) 2013, Maxime Biais <maxime@biais.org>

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
from arbitrage import config
from arbitrage.private_markets.market import Market, TradeException
from bcex.core.bcex_interface import BcexInterface
from bcex.core.websocket_client import Environment, Channel
from bcex.core.orders import OrderSide


class PrivateBcexUSD(Market):
    balance_url = "https://www.bitstamp.net/api/balance/"
    buy_url = "https://www.bitstamp.net/api/buy/"
    sell_url = "https://www.bitstamp.net/api/sell/"

    def __init__(self):
        super().__init__()
        self.api_secret = config.bcex_api_secret
        self.get_info()
        self._client = BcexInterface(symbols=["BTC-USD"],env=Environment.PROD)
        self._client.connect()


    def buy(self, amount, price):
        """Create a buy limit order"""
        self._client.place_order("BTC-USD", OrderSide.BUY, price=price, quantity=amount)

    def _sell(self, amount, price):
        """Create a sell limit order"""
        self._client.place_order("BTC-USD", OrderSide.SELL, price=price, quantity=amount)

    def get_info(self):
        """Get balance"""
        balances = self._client.get_balances()
        self.btc_balance = float(balances["BTC"]["available"])
        self.usd_balance = float(balances["USD"]["available"])
