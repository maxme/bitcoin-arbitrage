# Copyright (C) 2013, Maxime Biais <maxime@biais.org>
# Heavily modified by Ryan Casey <ryepdx@gmail.com>

import public_markets
import observers
import config
import config_dynamic
import time
import logging
import json
from public_markets.marketchain import MarketChain
from public_markets import bitcoincentral_market, bitfinex_market, \
    bitstamp_market, btce_market, campbx_market, intersango_market, \
    kraken_market, mtgox_market
from observers import emailer, historydumper, logger, traderbot, \
    traderbotsim, websocket

class Arbitrer(object):
    """Grabs prices from the markets defined in the config file
    and does all the actual arbitrage calculations.

    """

    def __init__(self, config = config):
        self.observers = {}
        self.markets = []
        self.reload(config)        
        config_dynamic.updated.connect(self.reload)
        

    def reload(self, config):
        for observer_name, observer in self.observers.items():
            if observer_name not in config.observers:
                observer.shutdown()

        self.init_markets(config.markets)
        self.init_observers(config.observers)


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
        'Btce'

        """

        self.markets = []
        self.market_names = markets
        for market_name, currency_pairs in markets.items():
            market_class_name = market_name.lower() + "_market"
            exec('from public_markets import ' + market_class_name)
            
            for pair in currency_pairs:
                market = eval(market_class_name.lower() +
                    '.' + market_name +
                    '(amount_currency="%s", price_currency="%s")' % tuple(pair)
                )
                self.markets.append(market)

        self.init_marketchains()


    def init_marketchains(self):
        # Generate all the valid market chains.
        self.marketchains = []
        marketchains = [MarketChain(market, pivot = config.pivot_currency)\
            for market in self.markets \
            if market.uses(config.pivot_currency)
        ]

        for i in range(0, config.max_trade_path_length - 1):
            num_marketchains = len(marketchains)

            for j in range(0, num_marketchains):
                marketchain = marketchains.pop(0)

                if marketchain.is_complete():
                    marketchains.append(marketchain)
                else:
                    for market in self.markets:
                        if marketchain.can_append(market):
                            new_marketchain = marketchain.copy()
                            new_marketchain.append(market)
                            marketchains.append(new_marketchain)

        for marketchain in marketchains:
            if marketchain.is_complete():
                self.marketchains.append(marketchain)


    def init_observers(self, _observers):
        """Instantiates the observer classes and populates the observers list.

        Observers allow for asynchronous output and/or order execution when the
        `Arbitrer` object discovers profitable trades. 

        Positional args:
        _observers - A list of names of classes in the `observers` module.

        """

        self.observers = {}
        self.observer_names = _observers
        for observer_name in _observers:
            exec('import observers.' + observer_name.lower())
            observer = eval('observers.' + observer_name.lower() + '.' +
                            observer_name + '()')
            self.observers[observer_name] = observer


    def tickers(self):
        """Logs the prices on every market."""

        for market in self.markets:
            ticker=market.get_ticker()
            logging.debug(
                "ticker: %-10s ask: %8.2f %3s (%5.2f) - bid: %8.2f %3s (%5.2f)" %
                (market.name[:10],
                 ticker["ask"]["price"],market.price_currency,ticker["ask"]["amount"],
                 ticker["bid"]["price"],market.price_currency,ticker["bid"]["amount"]))


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

            for market in self.market_names:
                if market in depths:
                    market.depth = depths[market]
            self.tick()


    def tick(self):
        """Finds all arbitrage opportunities across all markets at the
        present moment, and sends the opportunities on to the observers.

        """
        # Alert observers to the fact that we've now begun a tick.
        # This allows them to, for example, instantiate an empty list
        # where they might keep profitable trades. 
        for observer in self.observers.values():
            observer.begin_opportunity_finder(self.markets)


        # Build up our list of profitable trade chains.
        for chain in self.marketchains:
            tradechains = []
            chain.begin_transaction()
            tradechain = chain.next()

            while (config.perc_thresh
            and tradechain.percentage > config.perc_thresh) \
            or (config.profit_thresh
            and tradechain.profit > config.profit_thresh):
                tradechains.append(tradechain)
                tradechain = chain.next()

            if len(tradechains) > 0:
                # Notify our observers of the opportunities in this chain.
                for observer in self.observers.values():
                    observer.opportunity(tradechains)

            chain.end_transaction()

        # Let our observers know we're done feeding them opportunities.
        for observer in self.observers.values():
            observer.end_opportunity_finder()


    def loop(self):
        """Find arbitrage opportunities forever. (infinite loop)"""
        time_to_wait = sorted([m.update_rate for m in self.markets], reverse=True)[0]
        while True:
            self.tickers()
            self.tick()
            time.sleep(max(config.refresh_rate, time_to_wait))
