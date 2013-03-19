import urllib2
import json
import logging
from market import Market


class MtGoxEUR(Market):
    def __init__(self):
        super(MtGoxEUR, self).__init__("EUR")
        self.update_rate = 60

    def update_depth(self):
        res = urllib2.urlopen('https://data.mtgox.com/api/0/data/getDepth.php?Currency=EUR')
        jsonstr = res.read()
        try:
            depth = json.loads(jsonstr)
            self.depth = self.format_depth(depth)
        except Exception:
            logging.warn("Can't parse json:" + jsonstr)

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
    market = MtGoxEUR()
    print market.get_depth()
