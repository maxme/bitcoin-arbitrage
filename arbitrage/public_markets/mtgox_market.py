import urllib.request
import urllib.error
import urllib.parse
import json
import logging
from .market import Market


#FIXME (MDE) use Requests : https://pypi.python.org/pypi/requests
# and add gzip encoding
#install pip http://guide.python-distribute.org/installation.html#pip-installs-python-pip

#FIXME passer sur du Decimal partout !!


class MtGox(Market):
    def __init__(self, **kwargs):
        super(MtGox, self).__init__(**kwargs)
        self.trade_fee = 0.0060     # more complex than that https://www.mtgox.com/fee-schedule
        self.depth = {'asks': [{'price': 0, 'amount': 0}], 'bids': [
            {'price': 0, 'amount': 0}]}

    def update_depth(self):
        res = urllib.request.urlopen(
            'http://data.mtgox.com/api/2/%s%s/money/depth' % (
                self.amount_currency, self.price_currency
            )
        )
        jsonstr = res.read().decode('utf8')
        try:
            data = json.loads(jsonstr)
        except Exception:
            logging.error("%s - Can't parse json: %s" % (self.name, jsonstr))
        if data["result"] == "success":
            self.depth = self.format_depth(data["data"])
        else:
            logging.error("%s - fetched data error" % (self.name))

    def sort_and_format(self, l, reverse=False):
        l.sort(key=lambda x: float(x["price"]), reverse=reverse)
        r = []
        for i in l:
            r.append({'price': float(i[
                "price"]), 'amount': float(i["amount"])})
        return r

    def format_depth(self, depth):
        bids = self.sort_and_format(depth['bids'], True)
        asks = self.sort_and_format(depth['asks'], False)
        return {'asks': asks, 'bids': bids}


if __name__ == "__main__":
    market = MtGox()
    print(market.get_depth())
