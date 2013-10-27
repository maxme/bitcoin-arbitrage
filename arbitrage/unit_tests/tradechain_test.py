import sys

sys.path.append('../')
import unittest

from arbitrage.public_markets.trade import Trade
from arbitrage.public_markets.tradechain import TradeChain

class TestTradeChain(unittest.TestCase):
    def setUp(self):
        self.chain = TradeChain()

    def test_profit_functions(self):
        some_market = "A market name"
        self.chain.add_trade(Trade(some_market
            ).trade_from(3.28, "USD"
            ).trade_to(0.1, "BTC")
        )

        self.chain.add_trade(Trade(some_market
            ).trade_from(0.1, "BTC"
            ).trade_to(2, "LTC")
        )

        self.chain.add_trade(Trade(some_market
            ).trade_from(2, "LTC"
            ).trade_to(4, "USD")
        )

        assert float(self.chain.profit) == 0.72
        assert float(self.chain.percentage) == 0.22
