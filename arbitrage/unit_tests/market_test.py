import sys

sys.path.append('../')
import unittest

from arbitrage.public_markets.market import Market
from arbitrage.unit_tests.mockmarket import MockMarket

depth_bad = \
    {'asks': [{'amount': 4, 'price': 32.8},
              {'amount': 8, 'price': 32.9},
              {'amount': 2, 'price': 33.0},
              {'amount': 3, 'price': 33.6}],
     'bids': [{'amount': 2, 'price': 33.8},
              {'amount': 4, 'price': 31.6},
              {'amount': 6, 'price': 31.4},
              {'amount': 2, 'price': 30.1}]}

depth_ok = \
    {'asks': [{'amount': 4, 'price': 32.8},
              {'amount': 8, 'price': 32.9},
              {'amount': 2, 'price': 33.0},
              {'amount': 3, 'price': 33.6}],
     'bids': [{'amount': 2, 'price': 31.8},
              {'amount': 4, 'price': 31.6},
              {'amount': 6, 'price': 31.4},
              {'amount': 2, 'price': 30.1}]}


class TestMarket(unittest.TestCase):
    def setUp(self):
        self.market = MockMarket()

    def test_getdepth_invaliddata(self):
        self.market.set_mock_depth(depth_bad)
        self.market.get_depth()
        assert self.market.depth['asks'][0]['price'] == 0

    def test_getdepth_validdata(self):
        self.market.set_mock_depth(depth_ok)
        self.market.get_depth()
        assert self.market.depth['asks'][0]['price'] == 32.8
        assert self.market.depth['bids'][0]['price'] == 31.8


if __name__ == '__main__':
    unittest.main()
