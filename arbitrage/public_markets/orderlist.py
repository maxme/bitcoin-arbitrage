from decimal import Decimal

class Orderlist(object):
    """Allows for advancing down either a list of asks or a list of bids
    in small increments, returning the proceeds. Not an iterable, though.

    """

    def __init__(self, orders, amount_currency=None, price_currency=None):
        """Instantiates a list of orders for the `amount_currency` denominated
        in the `price_currency`

        Args:
        orders - A list of dictionaries with 'amount' and 'price' keys.
        amount_currency - The currency referred to in an order's 'amount'.
        from_current - The currency referred to in an order's 'price'.

        """

        if not amount_currency or not price_currency:
            raise Exception("Must define a amount_currency and a price_currency!")

        self.amount_currency = amount_currency
        self.price_currency = price_currency
        self.orders = orders


    def uses(self, currency):
        """Returns true if the currency is in this object's currency pair."""
        return (currency == self.amount_currency
        or currency == self.price_currency)


    def volume_to_next_price_as(self, currency):
        """Returns the amount of a given currency required to fill the order
        currently on top of the list and bring the next one up.

        Args:
        currency - The currency to denominate the volume in.

        """

        if currency == self.amount_currency:
            return self.orders[0]["amount"]
        elif currency == self.price_currency:
            return float(Decimal(str(self.orders[0]["price"])) * Decimal(str(self.orders[0]["amount"])))
        else:
            self._raise_currency_exception(currency)

 
    def evaluate_trade_volume(self, volume, currency):
        """Returns the amount of currency that would be yielded if the trade
        volume, denominated in `currency`, would yield if it were executed.
        Does not handle volumes that exceed the top order's volume at the
        moment, as such functionality is not yet necessary for our purposes.

        Args:
        volume - The amount of the given currency to remove from the top.
        currency - The currency denomination of the volume.

        """

        if currency == self.amount_currency:
            gross = Decimal(str(volume)) * Decimal(str(self.orders[0]["price"]))

        elif currency == self.price_currency:
            gross = Decimal(str(volume)) / Decimal(str(self.orders[0]["price"]))
                
        else:
            self._raise_currency_exception(currency)

        return float(gross.quantize(Decimal('1.00000000')))


    def execute_trade_volume(self, volume, currency):
        """Removes the given amount of the given currency from the top of the
        order list. Does not handle volumes that exceed the top order's volume
        at the moment, as such functionality is not yet necessary for our
        purposes.

        Args:
        volume - The amount of the given currency to remove from the top.
        currency - The currency denomination of the volume.

        """

        gross = self.evaluate_trade_volume(volume, currency)

        if currency == self.amount_currency:
            self.orders[0]["amount"] -= volume

        elif currency == self.price_currency:
            self.orders[0]["amount"] -= gross

        if self.orders[0]["amount"] <= 0:
            self.orders.pop(0)

        return gross


    def _raise_currency_exception(self, currency):
        """Raises an exception stating the currency isn't supported."""

        raise Exception("Unsupported currency: %s. Require %s or %s." % (
            currency, self.amount_currency, self.price_currency
        ))
