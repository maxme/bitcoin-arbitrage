import sys

sys.path.append('../')
import unittest

from arbitrage.public_markets.orderlist import Orderlist

depth = \
    {'asks': [{'amount': 4, 'price': 32.8},
              {'amount': 8, 'price': 32.9},
              {'amount': 2, 'price': 33.0},
              {'amount': 3, 'price': 33.6}],
     'bids': [{'amount': 2, 'price': 31.8},
              {'amount': 4, 'price': 31.6},
              {'amount': 6, 'price': 31.4},
              {'amount': 2, 'price': 30.1}]}


class TestOrderlist(unittest.TestCase):
    def setUp(self):
        self.orderlist = Orderlist(depth["asks"],
            price_currency="USD", amount_currency="BTC"
        )


    def test_validation_functions(self):
        assert self.orderlist.uses("USD")
        assert self.orderlist.uses("BTC")
        assert not self.orderlist.uses("LTC")


    def test_volume_functions(self):
        # Should match the figures from the first order in the list.
        assert self.orderlist.volume_to_next_price_as("BTC") == 4
        assert self.orderlist.volume_to_next_price_as("USD") == 131.2

        # Make sure it returns the amount of USD that 0.1 BTC would obtain.
        assert self.orderlist.evaluate_trade_volume(0.1, "BTC") == 3.28   
 
        # Make sure it returns the amount of BTC that 65.60 USD would obtain.
        assert self.orderlist.evaluate_trade_volume(65.60, "USD") == 2       
 
        # Make sure it returns the amount of BTC obtained from 65.60 USD.
        assert self.orderlist.execute_trade_volume(65.60, "USD") == 2
        
        # Should have half the original figure left.
        assert self.orderlist.volume_to_next_price_as("BTC") == 2
        assert self.orderlist.volume_to_next_price_as("USD") == 65.6
        
        # Make sure it returns the amount of USD obtained from 2 BTC.
        assert self.orderlist.execute_trade_volume(2, "BTC") == 65.6

        # Should match the figures from the second order in the list now.
        assert self.orderlist.volume_to_next_price_as("BTC") == 8
        assert self.orderlist.volume_to_next_price_as("USD") == 263.2

