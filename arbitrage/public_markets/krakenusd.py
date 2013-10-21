from ._kraken import Kraken

class KrakenUSD(Kraken):
    def __init__(self):
        super().__init__("USD", "XXBTZUSD")
