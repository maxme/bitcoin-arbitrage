from decimal import Decimal, ROUND_HALF_DOWN

class TradeChain(object):
    """Takes a series of trades and figures out the profit."""

    def __init__(self):
        self.trades = []

    def add_trade(self, trade):
        self.trades.append(trade)

    def scale(self, scaling_factor):
        for trade in self.trades:
            trade.from_volume = float(
                Decimal(str(trade.from_volume)) * Decimal(str(scaling_factor))
            )
            trade.to_volume = float(
                Decimal(str(trade.to_volume)) * Decimal(str(scaling_factor))
            )

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
        if self.profit == 0:
            return 0

        return float(((Decimal(str(self.profit)) / Decimal(
            str(self.trades[0].from_volume)
            )) * Decimal('100')).quantize(
                Decimal('1.00'), rounding=ROUND_HALF_DOWN)
        )
    
    @property
    def pivot_currency(self):
        if len(self.trades) == 0:
            return None

        return self.trades[0].from_currency


    def __str__(self):
        repr = "profit: %f %s with trade path: " % (
            self.profit, self.pivot_currency
        )

        path = ""
        for trade in self.trades:
            path += "%s -> " % str(trade)

        repr += "%s profit ~%.2f%%" % (path, self.percentage)

        return repr
