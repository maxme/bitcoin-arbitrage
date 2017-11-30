from arbitrage.markets._okcoin import OKCoinBase


class OKCoinCNY(OKCoinBase):
    def __init__(self, config=None):
        super().__init__("CNY", "btc_cny", config)
