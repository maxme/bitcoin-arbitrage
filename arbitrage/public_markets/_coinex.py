import urllib.request
import urllib.error
import urllib.parse
import json
import sys
from arbitrage.public_markets.market import Market


class Coinex(Market):
    def __init__(self, currency, code,reverse_pair = False):
        super().__init__(currency)
        self.code = code
        self.update_rate = 0.5
        self.reverse_pair = reverse_pair
    def update_depth(self):
        url = 'https://api.coinex.com/v1/market/depth?market=' + self.code + '&limit=20&merge=0'
        req = urllib.request.Request(url, None, headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "*/*",
            "User-Agent": "curl/7.24.0 (x86_64-apple-darwin12.0)"})
        res = urllib.request.urlopen(req)
        depth = json.loads(res.read().decode('utf8'))
        depth = depth["data"]
        self.depth = self.format_depth(depth)

    def sort_and_format(self, l, reverse):

        r = []

        if self.reverse_pair:
            for i in l:
                o_price = float(i[0])
                o_amount = float(i[1])

                d_price = 1.0 / o_price
                d_amount = o_amount * o_price

                r.append({'price': d_price, 'amount': d_amount})
        else:
            for i in l:
                r.append({'price': float(i[0]), 'amount': float(i[1])})

        r.sort(key=lambda x: float(x['price']), reverse=reverse)
        return r

    def format_depth(self, depth):
        if self.reverse_pair:
            asks = self.sort_and_format(depth['bids'], False)
            bids = self.sort_and_format(depth['asks'], True)
        else:
            bids = self.sort_and_format(depth['bids'], True)
            asks = self.sort_and_format(depth['asks'], False)  
        return {'asks': asks, 'bids': bids}
