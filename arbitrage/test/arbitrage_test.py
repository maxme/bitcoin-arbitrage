import sys
sys.path.append('../')
import unittest

import arbitrage

depths1 = {
    'BitcoinCentralEUR':
    {'asks': [{'amount': 4, 'price': 32.8},
              {'amount': 8, 'price': 32.9},
              {'amount': 2, 'price': 33.0},
              {'amount': 3, 'price': 33.6}],
     'bids': [{'amount': 2, 'price': 31.8},
              {'amount': 4, 'price': 31.6},
              {'amount': 6, 'price': 31.4},
              {'amount': 2, 'price': 30}]},
    'MtGoxEUR':
    {'asks': [{'amount': 1, 'price': 34.2},
              {'amount': 2, 'price': 34.3},
              {'amount': 3, 'price': 34.5},
              {'amount': 3, 'price': 35.0}],
     'bids': [{'amount': 2, 'price': 33.2},
              {'amount': 3, 'price': 33.1},
              {'amount': 5, 'price': 32.6},
              {'amount': 10, 'price': 32.3}]}}

depths2 = {
    'BitcoinCentralEUR':
    {'asks': [{'amount': 4, 'price': 32.8},
              {'amount': 8, 'price': 32.9},
              {'amount': 2, 'price': 33.0},
              {'amount': 3, 'price': 33.6}]},
    'MtGoxEUR':
    {'bids': [{'amount': 2, 'price': 33.2},
              {'amount': 3, 'price': 33.1},
              {'amount': 5, 'price': 32.6},
              {'amount': 10, 'price': 32.3}]}}

depths3 = {
    'BitcoinCentralEUR':
    {'asks': [{'amount': 1, 'price': 34.2},
              {'amount': 2, 'price': 34.3},
              {'amount': 3, 'price': 34.5},
              {'amount': 3, 'price': 35.0}]},
    'MtGoxEUR':
    {'bids': [{'amount': 2, 'price': 33.2},
              {'amount': 3, 'price': 33.1},
              {'amount': 5, 'price': 32.6},
              {'amount': 10, 'price': 32.3}]}}


class TestArbitrage(unittest.TestCase):
    def setUp(self):
        self.arbitrer = arbitrage.Arbitrer()

    def test_getprofit1(self):
        self.arbitrer.depths = depths2
        profit, vol, wb, ws = self.arbitrer.get_profit_for(
            0, 0, 'BitcoinCentralEUR', 'MtGoxEUR')
        assert(80 == int(profit * 100))
        assert(vol == 2)

    def test_getprofit2(self):
        self.arbitrer.depths = depths2
        profit, vol, wb, ws = self.arbitrer.get_profit_for(
            2, 1, 'BitcoinCentralEUR', 'MtGoxEUR')
        assert(159 == int(profit * 100))
        assert(vol == 5)

    def test_getprofit3(self):
        self.arbitrer.depths = depths3
        profit, vol, wb, ws = self.arbitrer.get_profit_for(
            2, 1, 'BitcoinCentralEUR', 'MtGoxEUR')
        assert(profit == 0)
        assert(vol == 0)

if __name__ == '__main__':
    unittest.main()
