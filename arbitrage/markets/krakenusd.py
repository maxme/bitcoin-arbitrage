from arbitrage.markets._kraken import KrakenBase


class KrakenUSD(KrakenBase):
    def __init__(self, config=None):
        super().__init__("USD", "XXBTZUSD", config)
