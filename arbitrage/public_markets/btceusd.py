import urllib.request
import urllib.error
import urllib.parse
import json
from .btce_market import BtceMarket


class BtceUSD(BtceMarket):
    def __init__(self):
        super(BtceUSD, self).__init__(to_currency="USD", from_currency="BTC")

if __name__ == "__main__":
    market = BtceUSD()
    print(market.get_ticker())
