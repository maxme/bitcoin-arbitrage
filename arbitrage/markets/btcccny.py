from arbitrage.markets._btcc import BTCCBase


class BTCCCNY(BTCCBase):
    def __init__(self, config=None):
        super().__init__("CNY", "btccny", config)
