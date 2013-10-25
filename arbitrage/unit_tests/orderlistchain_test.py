import sys

sys.path.append('../')
import unittest

from arbitrage.public_markets.orderlist import Orderlist
from arbitrage.public_markets.orderlistchain import OrderlistChain

depthUSDBTC = \
    {'asks': [{'amount': 4, 'price': 32.8},
              {'amount': 8, 'price': 32.9},
              {'amount': 2, 'price': 33.0},
              {'amount': 3, 'price': 33.6}]
    }

depthLTCBTC = \
    {'asks': [{'amount': 3, 'price': 0.05},
              {'amount': 1, 'price': 0.055},
              {'amount': 2, 'price': 0.06}]
    }

depthLTCUSD = \
    {'bids': [{'amount': 2, 'price': 2.00},
              {'amount': 1, 'price': 1.98},
              {'amount': 1, 'price': 1.00}]
    }


class TestOrderlistChain(unittest.TestCase):
    def setUp(self):
        self.orderlist1 = Orderlist(depthUSDBTC["asks"],
            price_currency="USD", amount_currency="BTC"
        )

        self.orderlist2 = Orderlist(depthLTCBTC["asks"],
            price_currency="BTC", amount_currency="LTC"
        )

        self.orderlist3 = Orderlist(depthLTCUSD["bids"],
            amount_currency="LTC", price_currency="USD"
        )

        self.chain = OrderlistChain(
            self.orderlist1, self.orderlist2, self.orderlist3
        )

    def test_profit_functions(self):
        tradechain = self.chain.next()
        assert tradechain.profit == 0.72
        assert tradechain.percentage == 0.22
        
        tradechain = self.chain.next()
        assert tradechain.profit == 0.34
        assert tradechain.percentage == 0.21

        tradechain = self.chain.next()
        assert tradechain.profit == -0.804
        assert tradechain.percentage == -0.45
