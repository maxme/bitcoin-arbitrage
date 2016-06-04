from ._huobi import Huobi

class HuobiCNY(Huobi):
    def __init__(self):
        super().__init__("CNY", "btc")
