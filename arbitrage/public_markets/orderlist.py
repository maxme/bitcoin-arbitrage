class Orderlist(object):
    """Allows for advancing down either a list of asks or a list of bids
    in small increments, returning the proceeds. Not an iterable, though.

    """

    def __init__(self, orders, to_currency=None, from_currency=None):
        """Instantiates a list of orders for the `to_currency` denominated
        in the `from_currency`

        Args:
        orders - A list of dictionaries with 'amount' and 'price' keys.
        to_currency - The currency referred to in an order's 'amount'.
        from_current - The currency referred to in an order's 'price'.

        """

        if not to_currency or not from_currency:
            raise Exception("Must define a to_currency and a from_currency!")

        self.to_currency = to_currency
        self.from_currency = from_currency
        self.orders = orders

    def volume_to_next_price_as(self, currency):
        """Returns the amount of a given currency required to fill the order
        currently on top of the list and bring the next one up.

        Args:
        currency - The currency to denominate the volume in.

        """

        if currency == self.to_currency:
            return self.orders[0]["amount"]
        elif currency == self.from_currency:
            return self.orders[0]["price"] * self.orders[0]["amount"]
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

        if currency == self.to_currency:
            gross = volume * self.orders[0]["price"]

        elif currency == self.from_currency:
            gross = volume / self.orders[0]["price"]
                
        else:
            self._raise_currency_exception(currency)

        return gross


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

        if currency == self.to_currency:
            self.orders[0]["amount"] -= volume

        elif currency == self.from_currency:
            self.orders[0]["amount"] -= gross

        if self.orders[0]["amount"] <= 0:
            self.orders.pop(0)

        return gross


    def _raise_currency_exception(self, currency):
        """Raises an exception stating the currency isn't supported."""

        raise Exception("Unsupported currency: %s. Require %s or %s." % (
            currency, self.to_currency, self.from_currency
        ))
