import urllib.request
import urllib.error
import urllib.parse
import json
from .market import Market


class CampBXUSD(Market):
    def __init__(self):
        super(CampBXUSD, self).__init__("USD")
        self.update_rate = 60

    def update_depth(self):
        res = urllib.request.urlopen('http://campbx.com/api/xdepth.php')
        depth = json.loads(res.read().decode('utf8'))
        self.depth = self.format_depth(depth)

    def sort_and_format(self, l, reverse=False):
        l.sort(key=lambda x: float(x[0]), reverse=reverse)
        r = []
        for i in l:
            r.append({'price': float(i[0]), 'amount': float(i[1])})
        return r

    def format_depth(self, depth):
        bids = self.sort_and_format(depth['Bids'], True)
        asks = self.sort_and_format(depth['Asks'], False)
        return {'asks': asks, 'bids': bids}

if __name__ == "__main__":
    market = CampBXUSD()
    print(market.get_ticker())
