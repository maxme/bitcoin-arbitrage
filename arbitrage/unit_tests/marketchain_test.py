import sys

sys.path.append('../')
import unittest

from arbitrage.unit_tests.mockmarket import MockMarket
from arbitrage.public_markets.marketchain import MarketChain

depthUSDBTC = \
    {'asks': [{'amount': 4, 'price': 32.8},
              {'amount': 8, 'price': 32.9},
              {'amount': 2, 'price': 33.0},
              {'amount': 3, 'price': 33.6}],
     'bids': [{'amount': 1, 'price': 31.8},
              {'amount': 7, 'price': 31.72},
              {'amount': 8, 'price': 31.5},
              {'amount': 6, 'price': 31.20}]
    }

depthLTCBTC = \
    {'asks': [{'amount': 3, 'price': 0.05},
              {'amount': 1, 'price': 0.055},
              {'amount': 2, 'price': 0.06}],
     'bids': [{'amount': 2, 'price': 0.045},
              {'amount': 5, 'price': 0.040},
              {'amount': 2, 'price': 0.03}]
    }

depthLTCUSD = \
    {'asks': [{'amount': 1, 'price': 2.10},
              {'amount': 2, 'price': 2.12},
              {'amount': 1, 'price': 3.00}],
     'bids': [{'amount': 2, 'price': 2.00},
              {'amount': 1, 'price': 1.98},
              {'amount': 1, 'price': 1.00}]
    }


class TestMarketChain(unittest.TestCase):
    def setUp(self):
        self.market1 = MockMarket(price_currency="USD", amount_currency="BTC")
        self.market1.set_mock_depth(depthUSDBTC)

        self.market2 = MockMarket(price_currency="BTC", amount_currency="LTC")
        self.market2.set_mock_depth(depthLTCBTC)

        self.market3 = MockMarket(amount_currency="LTC", price_currency="USD")
        self.market3.set_mock_depth(depthLTCUSD)

        self.chain = MarketChain(
            self.market1, self.market2, self.market3
        )

    def test_profit_functions(self):
        tradechain = self.chain.next()
        assert tradechain.profit == 0.72
        assert tradechain.percentage == 0.22
        
        # Make sure we're unlocked.
        assert not self.chain.locked
        
        self.chain.begin_transaction()    
    
        tradechain = self.chain.next()
        assert tradechain.profit == 0.34
        assert tradechain.percentage == 0.21
        
        # Make sure we're still locked.
        assert self.chain.locked

        tradechain = self.chain.next()
        assert tradechain.profit == -0.804
        assert tradechain.percentage == -0.45

        self.chain.end_transaction()

        # Make sure we're unlocked now.
        assert not self.chain.locked
