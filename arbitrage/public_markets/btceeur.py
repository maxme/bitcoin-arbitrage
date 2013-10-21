import urllib.request
import urllib.error
import urllib.parse
import json
from .btce_market import BtceMarket


class BtceEUR(BtceMarket):
    def __init__(self):
        super(BtceEUR, self).__init__(to_currency="EUR", from_currency="BTC")

if __name__ == "__main__":
    market = BtceEUR()
    print(market.get_ticker())
