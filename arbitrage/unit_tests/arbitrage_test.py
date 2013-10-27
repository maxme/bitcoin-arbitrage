import sys

sys.path.append('../')
import unittest

from arbitrage.arbitrer import Arbitrer

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
        self.arbitrer = Arbitrer()

if __name__ == '__main__':
    unittest.main()
