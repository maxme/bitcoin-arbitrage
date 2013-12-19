from collections import namedtuple
from public_markets.tradechain import TradeChain

# Allows us to keep track of exits and enterances in our chain of markets.
CurrencyPair = namedtuple("CurrencyPair", ['from_currency', 'to_currency'])

class MarketChain(object):
    def __init__(self, *args, pivot="USD"):
        self.locked = False
        self.markets = list(args)
        self.pivot_currency = pivot
        self.currency_pairs = []

        if not self.markets[0].uses(self.pivot_currency):
            raise Exception("Market chain doesn't begin with pivot currency!")

        if not self.markets[-1].uses(self.pivot_currency):
            raise Exception("Market chain doesn't end in pivot currency!")
        
        self.init_currency_pairs()

    def __str__(self):
        return "-->".join(["%s" % market for market in self.markets])

    def copy(self):
        new_marketchain = self
        new_marketchain.markets = self.markets[:]
        return new_marketchain

    def init_currency_pairs(self):
        if self.markets[0].price_currency == self.pivot_currency:
            self.currency_pairs = [CurrencyPair(
                from_currency = self.pivot_currency,
                to_currency = self.markets[0].amount_currency
            )]
        elif self.markets[0].amount_currency == self.pivot_currency:
            self.currency_pairs = [CurrencyPair(
                from_currency = self.pivot_currency,
                to_currency = self.markets[0].price_currency
            )]
        else:
            raise Exception("First Market in chain doesn't use pivot!")

        # Make sure we've been given a valid list of Markets.
        for i in range(0, len(self.markets)-1):
            from_pair = self.currency_pairs[i]
            to_market = self.markets[i+1]

            if not to_market.uses(from_pair.to_currency):
                raise Exception("Market discontinuity at self.markets[%i]" % i)
            
            # Remember the currency pairs we'll be trading to make it easier to build up
            # the TradeChain later.
            self.currency_pairs.append(CurrencyPair(
                to_currency = to_market.counter_currency(
                    from_pair.to_currency
                ),
                from_currency = from_pair.to_currency
            ))


    def can_append(self, market):
        if len(self.currency_pairs) == 0:
            return market.uses(self.pivot_currency)

        return market.chainable_with(
            self.markets[-1], exclude = [
                self.currency_pairs[-1].from_currency,
                self.pivot_currency
            ])


    def append(self, market):
        if not self.can_append(market):
            return False

        if len(self.currency_pairs) == 0:
            self.currency_pairs.append(CurrencyPair(
                from_currency = self.pivot_currency,
                to_currency = market.counter_currency(self.pivot_currency)
            ))
            self.markets.append(market)
            return True

        from_pair = self.currency_pairs[-1]
        self.currency_pairs.append(CurrencyPair(
            from_currency = from_pair.to_currency,
            to_currency = market.counter_currency(from_pair.to_currency)
        ))
        self.markets.append(market)
        return True


    def is_complete(self):
        return len(self.currency_pairs) > 1 \
        and self.currency_pairs[0].from_currency == self.pivot_currency \
        and self.currency_pairs[-1].to_currency == self.pivot_currency

    
    def begin_transaction(self):
        """Calls `begin_transaction` on all underlying Market objects."""
        self.locked = True
        for market in self.markets:
            market.begin_transaction()


    def end_transaction(self):
        """Calls `end_transaction` on all underlying Market objects."""
        self.locked = False
        for market in self.markets:
            market.end_transaction()


    def next(self):
        tradechain = TradeChain()

        # Lock all the markets so we can do a proper analysis,
        # if we are not already locked.
        already_locked = self.locked
        if not already_locked:
            self.begin_transaction()

        # Build up the trade chain, now that we know how much volume these
        # order books can take without (theoretically) changing prices on us.
        from_volume = self.largest_possible_volume()

        for i in range(0, len(self.markets)):
            pair = self.currency_pairs[i]
            trade = self.markets[i].execute_trade(
                from_volume, pair.from_currency
            )
            tradechain.add_trade(trade)

            from_volume = trade.to_volume

        # Unlock all the markets if we began this function locked.
        if not already_locked:
            self.end_transaction()
        
        return tradechain


    def largest_possible_volume(self):
        max_volume = None

        # Find the biggest trade volume possible without spanning bid or ask prices.
        for i in range(0, len(self.markets)-1):
            from_list = self.markets[i]
            to_list = self.markets[i+1]
            pair = self.currency_pairs[i]

            # Figure out which list has the smallest volume to the next price. 
            volume1 = from_list.r_volume_to_next_price_as(pair.to_currency)
            volume2 = to_list.volume_to_next_price_as(pair.to_currency)

            # Keep track of the maximum volume executable across order books
            # without changing the price. Eventually we want to end up with
            # a volume denominated in the chosen pivot currency.
            if not max_volume:
                max_volume = min(volume1, volume2)
            else:
                # Translate max_volume, which is currently denominated in the
                # currency we're moving from, to the currency we're moving to.
                # This allows for an accurate comparison. 
                max_volume = from_list.value_of(
                    pair.from_currency, volume = max_volume
                )
                max_volume = min(volume1, volume2, max_volume)

        max_volume = min(
            self.markets[-1].r_volume_to_next_price_as(self.currency_pairs[-1].to_currency),
            self.markets[-1].value_of(
                self.currency_pairs[-1].from_currency, volume = max_volume
            )
        )

        # Okay, now figure out how much we're supposed to put into the system
        # to get that amount out.
        for i in range(0, len(self.markets)):
            max_volume = self.markets[-1 * i].r_value_of(
                self.currency_pairs[-1 * i].to_currency, volume = max_volume
            )
        return max_volume

