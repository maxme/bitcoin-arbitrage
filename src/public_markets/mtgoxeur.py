import urllib2
import json
import logging
from market import Market

class MtGoxEUR(Market):
    def __init__(self):
        super(MtGoxEUR, self).__init__("EUR")
        self.update_rate = 60
        self.depth = {'asks': [{'price': 0, 'amount': 0}], 'bids': [{'price': 0, 'amount': 0}]}

    def update_depth(self):
	try:
            res = urllib2.urlopen('http://data.mtgox.com/api/2/BTCEUR/money/depth')
            jsonstr = res.read()
            try:
                data = json.loads(jsonstr)
            except Exception:
                logging.error("%s - Can't parse json: %s" % (self.name, jsonstr))
            if data["result"] == "success":
                self.depth = self.format_depth(data["data"])
            else:
                logging.error("%s - fetched data error" % (self.name))
	except Exception:
	    logging.error("%s - can't fetch data error" % (self.name))

    def sort_and_format(self, l, reverse=False):
        l.sort(key=lambda x: float(x["price"]), reverse=reverse)
        r = []
        for i in l:
            r.append({'price': float(i["price"]), 'amount': float(i["amount"])})
        return r

    def format_depth(self, depth):
        bids = self.sort_and_format(depth['bids'], True)
        asks = self.sort_and_format(depth['asks'], False)
        return {'asks': asks, 'bids': bids}

if __name__ == "__main__":
    market = MtGoxEUR()
    print market.get_depth()
