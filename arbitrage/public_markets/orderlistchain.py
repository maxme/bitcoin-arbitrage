from collections import namedtuple
from public_markets.tradechain import TradeChain

CurrencyPair = namedtuple("CurrencyPair", ['from_currency', 'to_currency'])

class OrderlistChain(object):
    def __init__(self, *args):
        self.orderlists = args
        self.currency_pairs = []
        
        # Make sure we've been given a valid list of Orderlists.
        for i in range(0, len(self.orderlists)-1):
            from_list = self.orderlists[i]
            to_list = self.orderlists[i+1]
            
            # Remember the currency pairs we'll be trading to make it easier to build up
            # the TradeChain later.
            # Figure out which currency we're moving to between lists.
            if to_list.uses(from_list.amount_currency):
                self.currency_pairs.append(CurrencyPair(
                    to_currency = from_list.amount_currency,
                    from_currency = from_list.price_currency
                ))
            elif to_list.used(from_list.price_currency):
                self.currency_pairs.append(CurrencyPair(
                    to_currency = from_list.price_currency,
                    from_currency = from_list.amount_currency
                ))
            else:
                raise Exception("Orderlist discontinuity detected at index "+i)

        if self.orderlists[0].uses(self.orderlists[-1].amount_currency):
            self.currency_pairs.append(CurrencyPair(
                to_currency = self.orderlists[-1].amount_currency,
                from_currency = self.orderlists[-1].price_currency
            ))
        elif self.orderlists[0].uses(self.orderlists[-1].price_currency):
            self.currency_pairs.append(CurrencyPair(
                to_currency = self.orderlists[-1].price_currency,
                from_currency = self.orderlists[-1].amount_currency
            ))
        else:
            raise Exception("Orderlist does not have a valid ending currency!")


    def next(self):
        tradechain = TradeChain()

        # Build up the trade chain, now that we know how much volume these
        # order books can take without (theoretically) changing prices on us.
        from_volume = self.largest_possible_volume()

        for i in range(0, len(self.orderlists)):
            pair = self.currency_pairs[i]
            to_volume = self.orderlists[i].execute_trade_volume(
                from_volume, pair.from_currency
            )

            tradechain.add_trade(
                {pair.from_currency: from_volume},
                {pair.to_currency: to_volume}
            )

            from_volume = to_volume

        return tradechain


    def largest_possible_volume(self):
        max_volume = None

        # Find the biggest trade volume possible without spanning bid or ask prices.
        for i in range(0, len(self.orderlists)-1):
            from_list = self.orderlists[i]
            to_list = self.orderlists[i+1]
            pair = self.currency_pairs[i]

            # Figure out which list has the smallest volume to the next price. 
            volume1 = from_list.volume_to_next_price_as(pair.to_currency)
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
                max_volume = from_list.evaluate_trade_volume(
                    max_volume, pair.from_currency
                )
                max_volume = min(volume1, volume2, max_volume)

        max_volume = min(
            self.orderlists[-1].volume_to_next_price_as(self.currency_pairs[-1].to_currency),
            self.orderlists[-1].evaluate_trade_volume(max_volume, self.currency_pairs[-1].from_currency)
        )

        # Okay, now figure out how much we're supposed to put into the system
        # to get that amount out.
        for i in range(0, len(self.orderlists)):
            max_volume = self.orderlists[-1 * i].evaluate_trade_volume(
                max_volume, self.currency_pairs[-1 * i].to_currency
            )
        return max_volume

