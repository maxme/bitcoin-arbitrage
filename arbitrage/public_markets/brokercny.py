# Copyright (C) 2016, Philsong <songbohr@gmail.com>

import urllib.request
import urllib.error
import urllib.parse
import json
from .market import Market
import lib.broker_api as exchange_api

class BrokerCNY(Market):
    def __init__(self):
        super().__init__('CNY')
        self.update_rate = 1

    def update_depth(self):
        depth = {}
        try:
            ticker = exchange_api.exchange_get_ticker()
            depth['asks'] = [[ticker.ask, 30]]
            depth['bids'] = [[ticker.bid, 30]]
        except Exception as e:
            exchange_api.re_init()
            return

        self.depth = self.format_depth(depth)

    def sort_and_format(self, l, reverse=False):
        l.sort(key=lambda x: float(x[0]), reverse=reverse)
        r = []
        for i in l:
            r.append({'price': float(i[0]), 'amount': float(i[1])})
        return r

    def format_depth(self, depth):
        bids = self.sort_and_format(depth['bids'], True)
        asks = self.sort_and_format(depth['asks'], False)
        return {'asks': asks, 'bids': bids}