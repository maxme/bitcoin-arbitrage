import sys

sys.path.append('../')
import unittest

from arbitrage.unit_tests.mockmarket import MockMarket

# Top bid is higher than top ask.
depth_bad = \
    {'asks': [{'amount': 4, 'price': 32.8},
              {'amount': 8, 'price': 32.9},
              {'amount': 2, 'price': 33.0},
              {'amount': 3, 'price': 33.6}],
     'bids': [{'amount': 2, 'price': 33.8},
              {'amount': 4, 'price': 31.6},
              {'amount': 6, 'price': 31.4},
              {'amount': 2, 'price': 30.1}]}

# Top bid is lower than top ask.
depth_ok = \
    {'asks': [{'amount': 4, 'price': 32.8},
              {'amount': 8, 'price': 32.9},
              {'amount': 2, 'price': 33.0},
              {'amount': 3, 'price': 33.6}],
     'bids': [{'amount': 2, 'price': 31.8},
              {'amount': 4, 'price': 31.6},
              {'amount': 6, 'price': 31.4},
              {'amount': 2, 'price': 30.1}]}

# Series of profitable trades on top, with one unprofitable trade.
depth_profit = \
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


    def test_validation_functions(self):
        assert self.market.uses("USD")
        assert self.market.uses("BTC")
        assert not self.market.uses("LTC")


    def test_invalid_execution(self):
        try:
            self.market.execute_trade(2, "BTC")
            assert False
        except Exception:
            assert True


    def test_volume_functions(self):
        self.market.set_mock_depth(depth_profit)

        # Lock the order book.
        self.market.begin_transaction()

        # Should match the figures from the first order in the list.
        assert self.market.volume_to_next_price_as("BTC") == 2
        assert self.market.volume_to_next_price_as("USD") == 131.2

        # Make sure it returns the amount of USD that 0.1 BTC would obtain.
        assert self.market.value_of("BTC", volume = 0.1) == 3.18   
 
        # Make sure it returns the amount of BTC that 65.60 USD would obtain.
        assert self.market.value_of("USD", volume = 65.60) == 2       
 
        # Make sure it returns the amount of BTC obtained from 65.60 USD.
        assert self.market.execute_trade(65.60, "USD").to_volume == 2
        
        # Should have half the original figure left in USD...
        assert self.market.volume_to_next_price_as("USD") == 65.6

        # ...and all the original figure left in BTC.        
        assert self.market.volume_to_next_price_as("BTC") == 2

        # Make sure it returns the amount of USD obtained from 2 BTC.
        assert self.market.execute_trade(2, "BTC").to_volume == 63.6

        # Clear out the top ask order.
        assert self.market.execute_trade(65.60, "USD").to_volume == 2

        # Should match the figures from the second order in the list now.
        assert self.market.volume_to_next_price_as("BTC") == 4 
        assert self.market.volume_to_next_price_as("USD") == 263.2

        self.market.end_transaction()


if __name__ == '__main__':
    unittest.main()
