from ._btcc import BTCC

class BTCCCNY(BTCC):
    def __init__(self):
        super().__init__("CNY", "btccny")
