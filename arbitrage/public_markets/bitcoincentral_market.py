import urllib.request
import urllib.error
import urllib.parse
import json
from .market import Market


class BitcoinCentral(Market):
    def update_depth(self):
        res = urllib.request.urlopen(
            'https://bitcoin-central.net/api/v1/depth?currency='
            + self.price_currency
        )
        depth = json.loads(res.read().decode('utf8'))
        self.depth = self.format_depth(depth)

    def sort_and_format(self, l, reverse=False):
        l.sort(key=lambda x: float(x['price']), reverse=reverse)
        r = []
        for i in l:
            r.append({'price': float(i[
                     'price']), 'amount': float(i['amount'])})
        return r

    def format_depth(self, depth):
        bids = self.sort_and_format(depth['bids'], True)
        asks = self.sort_and_format(depth['asks'], False)
        return {'asks': asks, 'bids': bids}

if __name__ == "__main__":
    market = BitcoinCentral()
    print(market.get_ticker())
