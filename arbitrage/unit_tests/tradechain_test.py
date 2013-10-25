import sys

sys.path.append('../')
import unittest

from arbitrage.public_markets.tradechain import TradeChain

class TestTradeChain(unittest.TestCase):
    def setUp(self):
        self.chain = TradeChain()

    def test_profit_functions(self):
        self.chain.add_trade({"USD": 3.28}, {"BTC": 0.1})
        self.chain.add_trade({"BTC": 0.1}, {"LTC": 2})
        self.chain.add_trade({"LTC": 2}, {"USD": 4})
        assert float(self.chain.profit) == 0.72
        assert float(self.chain.percentage) == 0.22
