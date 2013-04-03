import urllib.request
import urllib.error
import urllib.parse
import json
from .market import Market


class IntersangoEUR(Market):
    def __init__(self):
        super(IntersangoEUR, self).__init__("EUR")
        self.update_rate = 30

    def update_depth(self):
        res = urllib.request.urlopen(
            'https://intersango.com//api/depth.php?currency_pair_id=2')
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
    market = IntersangoEUR()
    print(json.dumps(market.get_ticker()))
