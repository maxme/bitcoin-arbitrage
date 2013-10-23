from ._kraken import Kraken

class KrakenEUR(Kraken):
    def __init__(self):
        super().__init__("EUR", "XXBTZEUR")
