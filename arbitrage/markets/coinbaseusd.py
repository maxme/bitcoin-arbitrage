from arbitrage.markets._coinbase import CoinBase


class CoinBaseUSD(CoinBase):
    def __init__(self, config=None):
        super().__init__("USD", "BTC-USD", config)
