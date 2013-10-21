import sys

sys.path.append('../')
import unittest

from arbitrage.public_markets.btce_market import BtceMarket

class TestBtcMarket(unittest.TestCase):
    def setUp(self):
        self.market = BtceMarket()

    def test_getdepth(self):
        self.market.get_depth()
        assert "asks" in self.market.depth
        assert "bids" in self.market.depth
        assert len(self.market.depth["asks"]) > 0
        assert len(self.market.depth["bids"]) > 0

        # Make sure none of the bids or asks are zero or less.
        # If they are, odds are something's broken!
        assert [x for x in self.market.depth["asks"] if x["price"] <= 0] == []
        assert [x for x in self.market.depth["bids"] if x["price"] <= 0] == []

if __name__ == '__main__':
    unittest.main()
