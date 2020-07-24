from arbitrage.public_markets._wbfex import WBFEx


class WBFExUSDT(WBFEx):
    def __init__(self):
        super().__init__("USD", "btcusdt")
