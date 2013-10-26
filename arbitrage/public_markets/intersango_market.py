import urllib.request
import urllib.error
import urllib.parse
import json
from .market import Market


class IntersangoMarket(Market):
    PAIR_IDS = {
        "BTC/GBP": "1",
        "BTC/EUR": "2",
        "BTC/USD": "3",
        "BTC/PLN": "4"
    }

    def __init__(self, **kwargs):
        super(IntersangoMarket, self).__init__(**kwargs)
        self.update_rate = 30
        self.pair_id = self._get_pair_id()

    def update_depth(self):
        res = urllib.request.urlopen(
            'https://intersango.com//api/depth.php?currency_pair_id='
            + self.pair_id
        )
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

    def _get_pair_id(self):
        pair = "%s/%s" % (self.amount_currency, self.price_currency)

        if pair not in PAIR_IDS:
            raise Exception("Invalid Intersango currency pair: %s" % pair)

        return self.PAIR_IDS[pair]

if __name__ == "__main__":
    market = IntersangoEUR()
    print(json.dumps(market.get_ticker()))
