import urllib.request
import urllib.error
import urllib.parse
import json
from arbitrage.markets.market import MarketBase


class PaymiumEUR(MarketBase):
    def __init__(self, config=None):
        super(PaymiumEUR, self).__init__("EUR", config)
        # bitcoin central maximum call / day = 5000
        # keep 2500 for other operations
        self.update_rate = 24 * 60 * 60 / 2500

    def update_depth(self):
        res = urllib.request.urlopen(
            'https://paymium.com/api/data/eur/depth')
        depth = json.loads(res.read().decode('utf8'))
        self.depth = self.format_depth(depth)

    def sort_and_format(self, l, reverse=False):
        l.sort(key=lambda x: float(x['price']), reverse=reverse)
        r = []
        for i in l:
            r.append({'price': float(i[
                                         'price']),
                      'amount': float(i['amount'])})
        return r

    def format_depth(self, depth):
        bids = self.sort_and_format(depth['bids'], True)
        asks = self.sort_and_format(depth['asks'], False)
        return {'asks': asks, 'bids': bids}


if __name__ == "__main__":
    market = PaymiumEUR()
    print(market.get_ticker())
