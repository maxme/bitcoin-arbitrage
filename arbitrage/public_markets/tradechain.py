from decimal import Decimal, ROUND_HALF_DOWN

class TradeChain(object):
    """Takes a series of trades and figures out the profit."""

    def __init__(self):
        self.trades = []

    def add_trade(self, from_trade, to_trade):
        self.trades.append({"from": from_trade, "to": to_trade})

    @property
    def profit(self):
        """Returns the profit made with the chain of trades. Assumes that the
        chain of trades starts and ends in the same currency.

        """

        return float(Decimal(str(list(self.trades[-1]["to"].values())[0]))
            - Decimal(str(list(self.trades[0]["from"].values())[0]))
        )

    @property
    def percentage(self):
        """Returns the percentage profit made with the chain of trades. Assumes
        that the chain of trades starts and ends in the same currency.

        """

        return float((Decimal(str(self.profit)) / Decimal(
            str(list(self.trades[0]["from"].values())[0])
        )).quantize(Decimal('1.00'), rounding=ROUND_HALF_DOWN))
