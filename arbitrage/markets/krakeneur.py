from arbitrage.markets._kraken import KrakenBase


class KrakenEUR(KrakenBase):
    def __init__(self, config=None):
        super().__init__("EUR", "XXBTZEUR", config)
