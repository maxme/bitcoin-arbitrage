from .ripple import PrivateRipple
import config


class PrivateRippleEUR(PrivateRipple):
    def __init__(self):
        super().__init__()
        self.currency = "EUR"
        self.usd_balance = self.fc.convert(self.eur_balance, "EUR", "USD")
        self.issuer = config.ripple_EUR_issuer
