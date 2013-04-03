import urllib.request
import urllib.error
import urllib.parse
import json
import sys
from .market import Market


class BitstampEUR(Market):
    def __init__(self):
        super(BitstampEUR, self).__init__("EUR")
        # bitcoin central maximum call / day = 5000
        # keep 2500 for other operations
        self.update_rate = 24 * 60 * 60 / 2500

    def update_depth(self):
        res = urllib.request.urlopen('https://www.bitstamp.net/api/eur_usd/')
        self.eurusd = json.loads(res.read().decode('utf8'))
        if self.eurusd["buy"] == "None" or self.eurusd["sell"] == "None":
            raise Exception("Can't fetch Bitstamp EUR/USD convertion rate")
        res = urllib.request.urlopen(
            'https://www.bitstamp.net/api/order_book/')
        depth = json.loads(res.read().decode('utf8'))
        self.depth = self.format_depth(depth)

    def sort_and_format(self, l, reverse, rate):
        r = []
        for i in l:
            r.append({'price': float(i[0]) / rate, 'amount': float(i[1])})
        r.sort(key=lambda x: float(x['price']), reverse=reverse)
        return r

    def format_depth(self, depth):
        bids = self.sort_and_format(depth[
                                    'bids'], True, float(self.eurusd["buy"]))
        asks = self.sort_and_format(depth[
                                    'asks'], False, float(self.eurusd["sell"]))
        return {'asks': asks, 'bids': bids}

if __name__ == "__main__":
    market = BitstampEUR()
    print(market.get_ticker())
