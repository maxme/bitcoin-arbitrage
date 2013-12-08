from .ripple import PrivateRipple
import config


class PrivateRippleUSD(PrivateRipple):
    def __init__(self):
        super().__init__()
        self.currency = "USD"
        self.issuer = config.ripple_USD_issuer
