from ._coinbase import Coinbase

class CoinbaseUSD(Coinbase):
    def __init__(self):
        super().__init__("USD", "BTC-USD")
