import urllib.request
import urllib.error
import urllib.parse
import json

from arbitrage.markets.market import MarketBase


class BTCCBase(MarketBase):
    def __init__(self, currency, symbol, config=None):
        super().__init__(currency, config)
        self.symbol = symbol
        self.update_rate = 30

    def update_depth(self):
        url = 'https://data.btcc.com/data/orderbook?market=' + self.symbol
        req = urllib.request.Request(url, headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "*/*",
            "User-Agent": "curl/7.24.0 (x86_64-apple-darwin12.0)"})
        res = urllib.request.urlopen(req)
        depth = json.loads(res.read().decode('utf8'))
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
