import time
import urllib.request
import urllib.error
import urllib.parse
import config
import logging
from decimal import Decimal
from public_markets.trade import Trade
from copy import deepcopy

class Market(object):
    def __init__(self, price_currency="USD", amount_currency="BTC", update_rate=60):
        self.price_currency = price_currency
        self.amount_currency = amount_currency
        self.depth_updated = 0
        self.update_rate = update_rate
        self.trade_fee = 0
        self.locked = False

    @property
    def name(self):
        return self.__class__.__name__


    def begin_transaction(self):
        """Locks the orderbook so it doesn't change unexpectedly. Enables
        mutation via `execute_trade_volume`. Thus we can be sure that any
        locked Market object likely does *not* reflect the true state of
        the market, while any unlocked one likely does.
        """
        self.depth = self.get_depth()
        self.locked = True
        self._pretransaction_depth = deepcopy(self.depth)


    def end_transaction(self):
        """Unlocks the orderbook."""
        self.locked = False
        self.depth = self._pretransaction_depth
        self.depth = self.get_depth() # Refresh depth if it's gotten stale.


    def get_depth(self):
        if self.locked:
            return self.depth

        timediff = time.time() - self.depth_updated
        if timediff > self.update_rate:
            self.ask_update_depth()
        timediff = time.time() - self.depth_updated
        if timediff > config.market_expiration_time:
            logging.warning('Market: %s order book is expired' % self.name)
            self.depth = {
                'asks': [{'price': 0, 'amount': 0}],
                'bids': [{'price': 0, 'amount': 0}]
            }

        if 'asks' not in self.depth or 'bids' not in self.depth \
        or len(self.depth['asks']) == 0 or len(self.depth['bids']) == 0:
            self.depth = {
                'asks': [{'price': 0, 'amount': 0}],
                'bids': [{'price': 0, 'amount': 0}]
            }

        # weidenrinde: Some markets have bid>ask, so this check is not
        # correct.
        #if self.depth['bids'][0]['price'] > self.depth['asks'][0]['price']:
        #    logging.warning(('Market: %s order book ' % self.name) \
        #        + 'is invalid (bid>ask)')
        #    self.depth = {
        #        'asks': [{'price': 0, 'amount': 0}], 
        #        'bids': [{'price': 0, 'amount': 0}]
        #    }
        return self.depth


    def uses(self, currency):
        """Returns true if the currency is in this object's currency pair."""
        return (currency == self.amount_currency
        or currency == self.price_currency)


    def chainable_with(self, market, exclude = []):
        """Returns true if the two markets can be adjacent in a trade chain."""
        return market != self and (
            (self.uses(market.price_currency
                ) and market.price_currency not in exclude
            ) or (self.uses(market.amount_currency
                ) and market.amount_currency not in exclude
            )
        )


    def counter_currency(self, currency):
        return self.amount_currency if self.amount_currency != currency \
        else self.price_currency


    def add_fee(self, volume):
        return float(Decimal(str(volume)) - \
            (Decimal(str(self.trade_fee)) * Decimal(str(volume)))
        )


    def remove_fee(self, volume):
        return float((Decimal(1) - Decimal(str(self.trade_fee))) \
            * Decimal(str(volume))
        )


    def r_volume_to_next_price_as(self, currency):
        """Returns the amount of a given currency you would have to buy to fill
        the order currently on top of either the ask or bid list (depending on
        the given currency) and bring the next one up.

        Args:
        currency - The currency to denominate the volume in.

        """
        depth = self.get_depth()

        if currency == self.amount_currency:
            return self.add_fee(depth['asks'][0]["amount"])
        elif currency == self.price_currency:
            return self.add_fee(
                float(Decimal(str(depth['bids'][0]["price"])) * Decimal(
                str(depth['bids'][0]["amount"])
            )))
        else:
            self._raise_currency_exception(currency)


    def volume_to_next_price_as(self, currency):
        """Returns the amount of a given currency you would have to sell to fill
        the order currently on top of either the ask or bid list (depending on
        the given currency) and bring the next one up.

        Args:
        currency - The currency to denominate the volume in.

        """
        depth = self.get_depth()

        if currency == self.amount_currency:
            return self.add_fee(depth['bids'][0]["amount"])
        elif currency == self.price_currency:
            return self.add_fee(
                float(Decimal(str(depth['asks'][0]["price"])) * Decimal(
                str(depth['asks'][0]["amount"])
            )))
        else:
            self._raise_currency_exception(currency)


    def r_value_of(self, currency, volume = 1):
        """Returns the amount of currency necessary to return the given volume
        of the given currency.
        Useful for working backwards to the amount of money that needs to go
        into the system after working out the maximum trade volume across
        market order books.
        Does not handle volumes that exceed the top order's volume at the
        moment, as such functionality is not yet necessary for our purposes.

        Args:
        volume - The amount of the given currency to remove from the top.
        currency - The currency denomination of the volume.

        """
        if volume == 0:
            return 0

        depth = self.get_depth()

        if depth["bids"][0]["price"] == 0:
            return 0

        volume = self.remove_fee(volume)

        if currency == self.amount_currency:
            gross = Decimal(str(volume)) * Decimal(str(depth["asks"][0]["price"]))

        elif currency == self.price_currency:
            gross = Decimal(str(volume)) / Decimal(str(depth["bids"][0]["price"]))
                
        else:
            self._raise_currency_exception(currency)

        return float(gross.quantize(Decimal('1.00000000')))


    def value_of(self, currency, volume=1):
        """Returns the amount that would be yielded if the trade volume,
        denominated in `currency`, were executed.
        Does not handle volumes that exceed the top order's volume at the
        moment, as such functionality is not yet necessary for our purposes.

        Args:
        volume - The amount of the given currency to remove from the top.
        currency - The currency denomination of the volume.

        """
        if volume == 0:
            return 0

        depth = self.get_depth()

        if depth["asks"][0]["price"] == 0:
            return 0

        volume = self.add_fee(volume)

        if currency == self.amount_currency:
            gross = Decimal(str(volume)) * Decimal(str(depth["bids"][0]["price"]))

        elif currency == self.price_currency:
            gross = Decimal(str(volume)) / Decimal(str(depth["asks"][0]["price"]))
                
        else:
            self._raise_currency_exception(currency)

        return float(gross.quantize(Decimal('1.00000000')))


    def execute_trade(self, volume, currency):
        """Removes the given amount of the given currency from the top of the
        order list. Does not handle volumes that exceed the top order's volume
        at the moment, as such functionality is not yet necessary for our
        purposes.

        Args:
        volume - The amount of the given currency to remove from the top.
        currency - The currency denomination of the volume.

        """
        if not self.locked:
            raise Exception("Cannot mutate orderbook outside a transaction.")

        gross = self.value_of(currency, volume = volume)

        if currency == self.amount_currency:
            trade_type = "sell"
            trade_price = self.depth['bids'][0]["price"]
            gross_currency = self.price_currency
            self.depth['bids'][0]["amount"] -= volume

        elif currency == self.price_currency:
            trade_type = "buy"
            trade_price = self.depth['asks'][0]["price"]
            gross_currency = self.amount_currency
            self.depth['asks'][0]["amount"] -= gross

        if self.depth['bids'][0]["amount"] <= 0:
            self.depth['bids'].pop(0)

        if self.depth['asks'][0]["amount"] <= 0:
            self.depth['asks'].pop(0)

        gross = float(Decimal(str(gross)) - Decimal(str(gross)
            ) * Decimal(str(self.trade_fee))
        )
        trade = Trade(self.name, trade_type, trade_price)

        return trade.trade_from(volume, currency
            ).trade_to(gross, gross_currency)


    def ask_update_depth(self):
        try:
            self.update_depth()
            self.depth_updated = time.time()
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            logging.error("HTTPError, can't update market: %s" % self.name)
        except Exception as e:
            logging.error("Can't update market: %s - %s" % (self.name, str(e)))

    def get_ticker(self):
        depth = self.get_depth()
        res = {'ask': 0, 'bid': 0}
        if len(depth['asks']) > 0 and len(depth["bids"]) > 0:
            res = {'ask': depth['asks'][0],
                   'bid': depth['bids'][0]}
        return res

    ## Abstract methods
    def update_depth(self):
        pass

    def buy(self, price, amount):
        pass

    def sell(self, price, amount):
        pass

    # Protected methods
    def _raise_currency_exception(self, currency):
        """Raises an exception stating the currency isn't supported."""
        raise Exception("Unsupported currency: %s. Require %s or %s." % (
            currency, self.amount_currency, self.price_currency
        ))
   
    def __str__(self):
        return "<%s(%s/%s)>" % (
            self.name, self.amount_currency, self.price_currency
        ) 
