# Copyright (C) 2013, Maxime Biais <maxime@biais.org>
# Heavily modified by Ryan Casey <ryepdx@gmail.com>

import public_markets
import observers
import config
import time
import logging
import json
from concurrent.futures import ThreadPoolExecutor, wait


class Arbitrer(object):
    """Grabs prices from the markets defined in the config file
    and does all the actual arbitrage calculations.

    """

    def __init__(self, config = config):
        self.markets = []
        self.observers = []
        self.depths = {}
        self.init_markets(config.markets)
        self.init_observers(config.observers)
        self.threadpool = ThreadPoolExecutor(max_workers=10)


    def init_markets(self, markets):
        """Instantiates the market classes and populates the markets list.

        Market objects provide currency pair prices, and trading fee data.

        Positional args:
        markets - A dictionary of exchange names
            mapped to lists of currency pair tuples.

        Example:

        >>> from types import SimpleNamespace
        >>> mock_config = SimpleNamespace(markets = [], observers = [])
        >>> arb = Arbitrer(config = mock_config)
        >>> arb.init_markets(mock_self, {"Btce": [("BTC", "USD")]})
        >>> arb.markets[0].name
        'BtceMarket'

        """

        self.market_names = markets
        for market_name, currency_pairs in markets.items():
            market_class_name = market_name.lower() + "_market"
            exec('import public_markets.' + market_class_name)
            
            for pair in currency_pairs:
                market = eval('public_markets.' + market_class_name.lower() +
                    '.' + market_name +
                    'Market(from_currency="%s", to_currency="%s")' % pair
                )
                self.markets.append(market)


    def init_observers(self, _observers):
        """Instantiates the observer classes and populates the observers list.

        Observers allow for asynchronous output and/or order execution when the
        `Arbitrer` object discovers profitable trades. 

        Positional args:
        _observers - A list of names of classes in the `observers` module.

        """

        self.observer_names = _observers
        for observer_name in _observers:
            exec('import observers.' + observer_name.lower())
            observer = eval('observers.' + observer_name.lower() + '.' +
                            observer_name + '()')
            self.observers.append(observer)


    def get_profit_for(self, mi, mj, kask, kbid):
        """Returns a tuple containing the profit, volume, selling price,
        and buying price for arbitrage between two given orders in the
        depths dictionary.

        Positional args:
        mi - The index of the trade in the `Arbitrer.depths` list for the
            exchange passed in as `kask`.
        mj - The index of the trade in the `Arbitrer.depths` list for the
            exchange passed in as `kbid`.
        kask - The name of the market to buy from.
        kbid - The name of the market to sell to.

        """
        # TODO: Remove assumption that all prices are in USD.
        if self.depths[kask]["asks"][mi]["price"] \
                >= self.depths[kbid]["bids"][mj]["price"]:
            return 0, 0, 0, 0

        max_amount_buy = 0
        for i in range(mi + 1):
            max_amount_buy += self.depths[kask]["asks"][i]["amount"]
        max_amount_sell = 0
        for j in range(mj + 1):
            max_amount_sell += self.depths[kbid]["bids"][j]["amount"]
        max_amount = min(max_amount_buy, max_amount_sell, config.max_tx_volume)

        buy_total = 0
        w_buyprice = 0
        for i in range(mi + 1):
            price = self.depths[kask]["asks"][i]["price"]
            amount = min(max_amount, buy_total + self.depths[
                kask]["asks"][i]["amount"]) - buy_total
            if amount <= 0:
                break
            buy_total += amount
            if w_buyprice == 0:
                w_buyprice = price
            else:
                # Calculate the average ask price for the profitable
                # orders we found.
                w_buyprice = (w_buyprice * (
                    buy_total - amount) + price * amount) / buy_total

        sell_total = 0
        w_sellprice = 0
        for j in range(mj + 1):
            price = self.depths[kbid]["bids"][j]["price"]
            amount = min(max_amount, sell_total + self.depths[
                kbid]["bids"][j]["amount"]) - sell_total
            if amount < 0:
                break
            sell_total += amount
            if w_sellprice == 0 or sell_total == 0:
                w_sellprice = price
            else:
                # Calculate the average bid price for the profitable
                # orders we found.
                w_sellprice = (w_sellprice * (
                    sell_total - amount) + price * amount) / sell_total

        profit = sell_total * w_sellprice - buy_total * w_buyprice
        return profit, sell_total, w_buyprice, w_sellprice


    def get_max_depth(self, kask, kbid):
        """Returns a tuple containing the maximum number of profitable
        arbitrage trades executable by only using the top ask and bid
        orders on the `Arbitrer.depths` lists for the given exchanges.

        Positional args:
        kask - The name of the market to buy from.
        kbid - The name of the market to sell to.

        """
        # TODO: Remove assumption that all prices are in USD.

        i = 0
        if len(self.depths[kbid]["bids"]) != 0 and \
                        len(self.depths[kask]["asks"]) != 0:
            while self.depths[kask]["asks"][i]["price"] \
                    < self.depths[kbid]["bids"][0]["price"]:
                if i >= len(self.depths[kask]["asks"]) - 1:
                    break
                i += 1
        j = 0
        if len(self.depths[kask]["asks"]) != 0 and \
                        len(self.depths[kbid]["bids"]) != 0:
            while self.depths[kask]["asks"][0]["price"] \
                    < self.depths[kbid]["bids"][j]["price"]:
                if j >= len(self.depths[kbid]["bids"]) - 1:
                    break
                j += 1
        return i, j


    def arbitrage_opportunity(self, kask, kbid):
        """Finds all profitable trades and passes on trade profit information
        to all observers.

        Positional args:
        kask - The name of the market to use for ask prices.
        kbid - The name of the market to use for bid prices.

        """

        # TODO: Remove assumption that all prices are in USD.
        profit, volume, buyprice, sellprice, weighted_buyprice, \
        weighted_sellprice = self.arbitrage_depth_opportunity(kask, kbid)
        if volume == 0 or buyprice == 0:
            return
        perc2 = (1 - (volume - (profit / buyprice)) / volume) * 100
        for observer in self.observers:
            observer.opportunity(
                profit, volume, buyprice, kask, sellprice, kbid,
                perc2, weighted_buyprice, weighted_sellprice)


    def arbitrage_depth_opportunity(self, kask, kbid):
        """Goes down the order book defined in `Arbitrer.depths` and returns
        the profit realized, volume required, averaged buy and sell prices,
        and the buy and sell prices on most profitable trade pair in the
        exchange books of the markets passed in.

        Positional args:
        kask - The name of the market to grab ask prices from.
        kbid - The name of the market to grab bid prices from.
        
        """

        # TODO: Remove assumption that all prices are in USD.
        maxi, maxj = self.get_max_depth(kask, kbid)
        best_profit = 0
        best_i, best_j = (0, 0)
        best_w_buyprice, best_w_sellprice = (0, 0)
        best_volume = 0
        for i in range(maxi + 1):
            for j in range(maxj + 1):
                profit, volume, w_buyprice, w_sellprice = self.get_profit_for(
                    i, j, kask, kbid)
                if profit >= 0 and profit >= best_profit:
                    best_profit = profit
                    best_volume = volume
                    best_i, best_j = (i, j)
                    best_w_buyprice, best_w_sellprice = (
                        w_buyprice, w_sellprice)
        return best_profit, best_volume, \
               self.depths[kask]["asks"][best_i]["price"], \
               self.depths[kbid]["bids"][best_j]["price"], \
               best_w_buyprice, best_w_sellprice


    def __get_market_depth(self, market, depths):
        """A callback used by `Arbitrer.update_depths` to asynchronously fetch
        market depths.

        """
        depths[market.name] = market.get_depth()


    def update_depths(self):
        """Asynchronously grabs the order books from all markets in
        `Arbitrer.markets` and returns a `depths` dictionary.

        """

        depths = {}
        futures = []
        for market in self.markets:
            futures.append(self.threadpool.submit(self.__get_market_depth,
                                                  market, depths))
        wait(futures, timeout=20)
        return depths


    def tickers(self):
        """Logs the prices on every market."""

        for market in self.markets:
            logging.debug("ticker: " + market.name + " - " + str(
                market.get_ticker()))


    def replay_history(self, directory):
        """Takes the path of a directory containing JSON files named in such
        a way that a naive sort by filename puts them in chronological order
        and steps through them, treating each JSON file as a snapshot of the
        market depths at a single point in time, and calculating arbitrage
        profitability.

        Running the bot with the HistoryDumper observer enabled will generate
        JSON files that can be used to replay the market movements that
        occurred while the bot was running.

        Positional args:
        directory - The path to the directory containing the market history
        JSON files.

        """
        import os
        import json
        import pprint

        files = os.listdir(directory)
        files.sort()
        for f in files:
            depths = json.load(open(directory + '/' + f, 'r'))
            self.depths = {}
            for market in self.market_names:
                if market in depths:
                    self.depths[market] = depths[market]
            self.tick()


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
                        self.arbitrage_opportunity(kmarket1, kmarket2)

        for observer in self.observers:
            observer.end_opportunity_finder()


    def loop(self):
        """Find arbitrage opportunities forever. (infinite loop)"""
        time_to_wait = sorted([m.update_rate for m in self.markets], reverse=True)[0]
        while True:
            self.depths = self.update_depths()
            self.tickers()
            self.tick()
            time.sleep(max(config.refresh_rate, time_to_wait))
