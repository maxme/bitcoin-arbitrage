import urllib.request
import urllib.error
import urllib.parse
import json
from arbitrage.markets.market import MarketBase


class KrakenBase(MarketBase):
    def __init__(self, currency, code, config=None):
        super().__init__(currency, config)
        self.code = code
        self.update_rate = 30

    def update_depth(self):
        url = 'https://api.kraken.com/0/public/Depth'
        req = urllib.request.Request(url, b"pair=" + bytes(self.code, "ascii"),
                                     headers={
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
        bids = self.sort_and_format(depth['result'][self.code]['bids'], True)
        asks = self.sort_and_format(depth['result'][self.code]['asks'], False)
        return {'asks': asks, 'bids': bids}
