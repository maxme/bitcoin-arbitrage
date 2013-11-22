from ._ripple import Ripple
import config

class RippleEUR(Ripple):
    def __init__(self):
        super().__init__("EUR", config.ripple_EUR_issuer)
