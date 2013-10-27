from decimal import Decimal, ROUND_HALF_DOWN

class TradeChain(object):
    """Takes a series of trades and figures out the profit."""

    def __init__(self):
        self.trades = []

    def add_trade(self, trade):
        self.trades.append(trade)

    @property
    def profit(self):
        """Returns the profit made with the chain of trades. Assumes that the
        chain of trades starts and ends in the same currency.

        """

        return float(Decimal(str(self.trades[-1].to_volume))
            - Decimal(str(self.trades[0].from_volume))
        )

    @property
    def percentage(self):
        """Returns the percentage profit made with the chain of trades. Assumes
        that the chain of trades starts and ends in the same currency.

        """

        return float((Decimal(str(self.profit)) / Decimal(
            str(self.trades[0].from_volume)
        )).quantize(Decimal('1.00'), rounding=ROUND_HALF_DOWN))
