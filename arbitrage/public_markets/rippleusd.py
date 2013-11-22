from ._ripple import Ripple
import config

class RippleUSD(Ripple):
    def __init__(self):
        super().__init__("USD", config.ripple_USD_issuer)
