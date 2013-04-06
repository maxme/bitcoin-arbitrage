import urllib.request
import urllib.error
import urllib.parse
import json
from .market import Market


class BitfloorUSD(Market):
    def __init__(self):
        super(BitfloorUSD, self).__init__("USD")
        self.update_rate = 60

    def update_depth(self):
        res = urllib.request.urlopen('https://api.bitfloor.com/book/L2/1')
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

if __name__ == "__main__":
    market = BitfloorUSD()
    print(market.get_ticker())
