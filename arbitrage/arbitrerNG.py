# Copyright (C) 2013, Maxime Biais <maxime@biais.org>

import public_markets
import observers
import config
import time
import logging
import json
from arbitrer import Arbitrer
from concurrent.futures import ThreadPoolExecutor, wait

#FIXME : intégrer les taxes du marché dans le calcul du meilleur profit
# en augmentant les volumes, on peut avoir un meilleur profit absolu, mais plus faible par rapport au montant de la transaction


class ArbitrerNG(Arbitrer):
    """Grabs prices from the markets defined in the config file
    and does all the actual arbitrage calculations.

    """

    def arbitrage_opportunity(self, kask, kbid, max_volume):
        """Finds all profitable trades and passes on trade profit information
        to all observers.

        Positional args:
        kask - The name of the market to use for ask prices.
        kbid - The name of the market to use for bid prices.

        """

        # TODO: Remove assumption that all prices are in USD.
        profit, volume, buyprice, sellprice, weighted_buyprice, \
        weighted_sellprice = self.arbitrage_depth_opportunity(kask, kbid, max_volume)
        if volume == 0 or profit == 0:
            return
        perc2 = (1 - (volume - (profit / buyprice)) / volume) * 100
        for observer in self.observers:
            observer.opportunity(
                profit, volume, buyprice, kask, sellprice, kbid,
                perc2, weighted_buyprice, weighted_sellprice)


    def arbitrage_depth_opportunity(self, kask, kbid, max_volume):
        """Goes down the order book defined in `Arbitrer.depths` and returns
        the profit realized, volume required, averaged buy and sell prices,
        and the buy and sell prices on most profitable trade pair in the
        exchange books of the markets passed in.

        Positional args:
        kask - The name of the market to grab ask prices from.
        kbid - The name of the market to grab bid prices from.
        
        """
        # to return :
        # profit, volume, buyprice, sellprice, weighted_buyprice, weighted_sellprice
        # TODO: Remove assumption that all prices are in USD.
        d_ask = self.depths[kask]['asks']
        d_bid = self.depths[kbid]['bids']

        cursor_ask = 0
        c_ask_amount = d_ask[cursor_ask]['amount']

        cursor_bid = 0
        c_bid_amount = d_bid[cursor_bid]['amount']

        best_profit = 0
        best_volume = 0
        best_ask = 0
        best_bid = 0

        total_volume = 0
        total_buy = 0
        total_sell = 0
        total_fee = 0

        fee_buy = list(filter(lambda m: m.name == kask, self.markets))[0].trade_fee
        fee_sell = list(filter(lambda m: m.name == kbid, self.markets))[0].trade_fee

        while True:
            v_to_buy = min(c_ask_amount, c_bid_amount, max_volume - total_volume)

            buy = v_to_buy * d_ask[cursor_ask]['price']
            sell = v_to_buy * d_bid[cursor_bid]['price']
            fee = buy * fee_buy + sell * fee_sell

            c_ask_amount -= v_to_buy
            c_bid_amount -= v_to_buy

            profit = sell - buy
            if profit <= 0:     # reached the max of possible arbitrage, get out
                break

            total_buy += buy
            total_sell += sell
            total_fee += fee
            total_profit = total_sell - total_buy - total_fee
            total_volume += v_to_buy

            if total_profit > best_profit:
                best_profit = total_profit
                best_volume = total_volume
                best_ask = cursor_ask
                best_bid = cursor_bid

            if total_volume == max_volume:  # reached the max of possible transaction
                break

            if c_ask_amount == 0:   # reached the max for the ask at this price -> step forward
                cursor_ask += 1
                c_ask_amount = d_ask[cursor_ask]['amount']

            if c_bid_amount == 0:   # reached the max for the bid at this price -> step forward
                cursor_bid += 1
                c_bid_amount = d_bid[cursor_bid]['amount']

        # to return :
        # profit, volume, buyprice, sellprice, weighted_buyprice, weighted_sellprice
        w_buy = 0 if total_volume == 0 else total_buy / total_volume
        w_sell = 0 if total_volume == 0 else total_sell / total_volume
        # FIXME : improve the result to take trade fee into account better
        return best_profit, best_volume, \
               d_ask[best_ask]['price'], d_bid[best_bid]['price'], \
               w_buy, w_sell


    def tick(self):
        """Finds all arbitrage opportunities across all markets at the
        present moment, and sends the opportunities on to the observers.

        """

        # Alert observers to the fact that we've now begun a tick.
        # This allows them to, for example, instantiate an empty list
        # where they might keep 
        for observer in self.observers:
            observer.begin_opportunity_finder(self.depths)

        for kmarket1 in self.depths:
            for kmarket2 in self.depths:
                if kmarket1 == kmarket2:  # same market
                    continue
                market1 = self.depths[kmarket1]
                market2 = self.depths[kmarket2]
                if market1["asks"] and market2["bids"] \
                    and len(market1["asks"]) > 0 and len(market2["bids"]) > 0:
                    if market1["asks"][0]['price'] < market2["bids"][0]['price']:
                        self.arbitrage_opportunity(kmarket1, kmarket2, config.max_tx_volume)

        for observer in self.observers:
            observer.end_opportunity_finder()
