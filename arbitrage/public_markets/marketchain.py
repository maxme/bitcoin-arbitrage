from collections import namedtuple
from public_markets.tradechain import TradeChain

# Allows us to keep track of exits and enterances in our chain of markets.
CurrencyPair = namedtuple("CurrencyPair", ['from_currency', 'to_currency'])

class MarketChain(object):
    def __init__(self, *args, pivot="USD"):
        self.locked = False
        self.markets = args
        self.pivot_currency = pivot
        self.currency_pairs = []

        if not self.markets[0].uses(self.pivot_currency):
            raise Exception("Market chain doesn't begin with pivot currency!")

        if not self.markets[-1].uses(self.pivot_currency):
            raise Exception("Market chain doesn't end in pivot currency!")
        
        if len(self.markets) > 1:
            self.init_currency_pairs()


    def init_currency_pairs(self):
        self.currency_pairs = []

        # Make sure we've been given a valid list of Markets.
        for i in range(0, len(self.markets)-1):
            from_list = self.markets[i]
            to_list = self.markets[i+1]
            
            # Remember the currency pairs we'll be trading to make it easier to build up
            # the TradeChain later.
            # Figure out which currency we're moving to between lists.
            if to_list.uses(from_list.amount_currency):
                self.currency_pairs.append(CurrencyPair(
                    to_currency = from_list.amount_currency,
                    from_currency = from_list.price_currency
                ))
            elif to_list.uses(from_list.price_currency):
                self.currency_pairs.append(CurrencyPair(
                    to_currency = from_list.price_currency,
                    from_currency = from_list.amount_currency
                ))
            else:
                raise Exception("Market discontinuity detected at index "+i)

        if self.markets[0].uses(self.markets[-1].amount_currency) \
        and self.markets[-1].amount_currency == self.pivot_currency:
            self.currency_pairs.append(CurrencyPair(
                to_currency = self.markets[-1].amount_currency,
                from_currency = self.markets[-1].price_currency
            ))
        elif self.markets[0].uses(self.markets[-1].price_currency) \
        and self.markets[-1].price_currency == self.pivot_currency:
            self.currency_pairs.append(CurrencyPair(
                to_currency = self.markets[-1].price_currency,
                from_currency = self.markets[-1].amount_currency
            ))

    
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
                max_volume = from_list.r_evaluate_trade_volume(
                    max_volume, pair.from_currency
                )
                max_volume = min(volume1, volume2, max_volume)

        max_volume = min(
            self.markets[-1].r_volume_to_next_price_as(self.currency_pairs[-1].to_currency),
            self.markets[-1].evaluate_trade_volume(max_volume, self.currency_pairs[-1].from_currency)
        )

        # Okay, now figure out how much we're supposed to put into the system
        # to get that amount out.
        for i in range(0, len(self.markets)):
            max_volume = self.markets[-1 * i].r_evaluate_trade_volume(
                max_volume, self.currency_pairs[-1 * i].to_currency
            )
        return max_volume

