# Copyright (C) 2013, Maxime Biais <maxime@biais.org>

import public_markets
import observers
import config
import time
import logging
import json
from concurrent.futures import ThreadPoolExecutor, wait

#FIXME : intégrer les taxes du marché dans le calcul du meilleur profit
# en augmentant les volumes, on peut avoir un meilleur profit absolu, mais plus faible par rapport au montant de la transaction



class ArbitrerNG(object):
    def __init__(self):
        self.markets = []
        self.observers = []
        self.depths = {}
        self.init_markets(config.markets)
        self.init_observers(config.observers)
        self.threadpool = ThreadPoolExecutor(max_workers=10)

    def init_markets(self, markets):
        self.market_names = markets
        for market_name in markets:
            exec('import public_markets.' + market_name.lower())
            market = eval('public_markets.' + market_name.lower() + '.' +
                          market_name + '()')
            self.markets.append(market)

    def init_observers(self, _observers):
        self.observer_names = _observers
        for observer_name in _observers:
            exec('import observers.' + observer_name.lower())
            observer = eval('observers.' + observer_name.lower() + '.' +
                            observer_name + '()')
            self.observers.append(observer)


    def arbitrage_opportunity(self, kask, kbid, max_volume):
        profit, volume, buyprice, sellprice, weighted_buyprice, weighted_sellprice = \
            self.arbitrage_depth_opportunity(kask, kbid, max_volume)
        if volume == 0 or profit == 0:
            return
        perc2 = (1 - (volume - (profit / buyprice)) / volume) * 100
        for observer in self.observers:
            observer.opportunity(
                profit, volume, buyprice, kask, sellprice, kbid,
                perc2, weighted_buyprice, weighted_sellprice)

    def arbitrage_depth_opportunity(self, kask, kbid, max_volume):
        # to return :
        # profit, volume, buyprice, sellprice, weighted_buyprice, weighted_sellprice

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

        while True:
            v_to_buy = min(c_ask_amount, c_bid_amount, max_volume - total_volume)

            buy = v_to_buy * d_ask[cursor_ask]['price']
            sell = v_to_buy * d_bid[cursor_bid]['price']

            c_ask_amount -= v_to_buy
            c_bid_amount -= v_to_buy

            profit = sell - buy
            if profit <= 0:     # reached the max of possible arbitrage, get out
                break

            total_buy += buy
            total_sell += sell
            total_profit = total_sell - total_buy
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
        return best_profit, best_volume, \
               d_ask[best_ask]['price'], d_bid[best_bid]['price'], \
               w_buy, w_sell

    def __get_market_depth(self, market, depths):
        depths[market.name] = market.get_depth()

    def update_depths(self):
        depths = {}
        futures = []
        for market in self.markets:
            futures.append(self.threadpool.submit(self.__get_market_depth,
                                                  market, depths))
        wait(futures, timeout=20)
        return depths

    def tickers(self):
        for market in self.markets:
            logging.debug("ticker: " + market.name + " - " + str(
                market.get_ticker()))

    def replay_history(self, directory):
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
                        self.arbitrage_opportunity(kmarket1, kmarket2, 10)
                        self.arbitrage_opportunity(kmarket1, kmarket2, 20)

        for observer in self.observers:
            observer.end_opportunity_finder()

    def loop(self):
        while True:
            self.depths = self.update_depths()
            self.tickers()
            self.tick()
            time.sleep(config.refresh_rate)
