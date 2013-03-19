import public_markets
import observers
import config
import time
import logging


class Arbitrer(object):
    def __init__(self):
        self.markets = []
        self.observers = []
        self.depths = {}
        self.init_markets(config.markets)
        self.init_observers(config.observers)

    def init_markets(self, markets):
        self.market_names = markets
        for market_name in markets:
            exec('import public_markets.' + market_name.lower())
            market = eval('public_markets.' + market_name.lower()
                          + '.' + market_name + '()')
            self.markets.append(market)

    def init_observers(self, observers):
        self.observer_names = observers
        for observer_name in observers:
            exec('import observers.' + observer_name.lower())
            observer = eval('observers.' + observer_name.lower()
                            + '.' + observer_name + '()')
            self.observers.append(observer)

    def get_profit_for(self, mi, mj, kask, kbid):
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
            amount = min(max_amount, buy_total
                         + self.depths[kask]["asks"][i]["amount"]) - buy_total
            if amount <= 0:
                break
            buy_total += amount
            if w_buyprice == 0:
                w_buyprice = price
            else:
                w_buyprice = (w_buyprice * (buy_total - amount)
                              + price * amount) / buy_total

        sell_total = 0
        w_sellprice = 0
        for j in range(mj + 1):
            price = self.depths[kbid]["bids"][j]["price"]
            amount = min(max_amount, sell_total
                         + self.depths[kbid]["bids"][j]["amount"]) - sell_total
            if amount < 0:
                break
            sell_total += amount
            if w_sellprice == 0:
                w_sellprice = price
            else:
                w_sellprice = (w_sellprice * (sell_total - amount)
                               + price * amount) / sell_total

        profit = sell_total * w_sellprice - buy_total * w_buyprice
        return profit, sell_total, w_buyprice, w_sellprice

    def get_max_depth(self, kask, kbid):
        i = 0
        if len(self.depths[kbid]["bids"]) != 0 \
                and len(self.depths[kask]["asks"]) != 0:
            while self.depths[kask]["asks"][i]["price"] \
                    < self.depths[kbid]["bids"][0]["price"]:
                if i >= len(self.depths[kask]["asks"]) - 1:
                    break
                i += 1
        j = 0
        if len(self.depths[kask]["asks"]) != 0 \
                and len(self.depths[kbid]["bids"]) != 0:
            while self.depths[kask]["asks"][0]["price"] \
                    < self.depths[kbid]["bids"][j]["price"]:
                if j >= len(self.depths[kbid]["bids"]) - 1:
                    break
                j += 1
        return i, j

    def arbitrage_depth_opportunity(self, kask, kbid):
        maxi, maxj = self.get_max_depth(kask, kbid)
        best_profit = 0
        best_i, best_j = (0, 0)
        best_w_buyprice, best_w_sellprice = (0, 0)
        best_volume = 0
        for i in range(maxi + 1):
            for j in range(maxj + 1):
                profit, volume, w_buyprice, w_sellprice = \
                    self.get_profit_for(i, j, kask, kbid)
                if profit >= 0 and profit >= best_profit:
                    best_profit = profit
                    best_volume = volume
                    best_i, best_j = (i, j)
                    best_w_buyprice, best_w_sellprice = (w_buyprice,
                                                         w_sellprice)
        return best_profit, best_volume, \
            self.depths[kask]["asks"][best_i]["price"], \
            self.depths[kbid]["bids"][best_j]["price"], \
            best_w_buyprice, best_w_sellprice

    def arbitrage_opportunity(self, kask, ask, kbid, bid):
        # perc = (bid["price"] - ask["price"]) \
        #    / bid["price"] * 100
        profit, volume, buyprice, sellprice, weighted_buyprice,\
            weighted_sellprice = self.arbitrage_depth_opportunity(kask, kbid)
        if volume == 0 or buyprice == 0:
            return
        perc2 = (1 - (volume - (profit / buyprice)) / volume) * 100
        for observer in self.observers:
            observer.opportunity(profit, volume, buyprice, kask,
                                 sellprice, kbid,
                                 perc2, weighted_buyprice, weighted_sellprice)

    def update_depths(self):
        depths = {}
        for market in self.markets:
            depths[market.name] = market.get_depth()
        return depths

    def tickers(self):
        for market in self.markets:
            logging.debug("ticker: " + market.name + " - "
                          + str(market.get_ticker()))

    def replay_history(self, directory):
        import os
        import json
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
                if float(market1["asks"][0]['price']) \
                        < float(market2["bids"][0]['price']):
                    self.arbitrage_opportunity(kmarket1, market1["asks"][0],
                                               kmarket2, market2["bids"][0])

        for observer in self.observers:
            observer.end_opportunity_finder()

    def loop(self):
        while True:
            self.depths = self.update_depths()
            self.tickers()
            self.tick()
            time.sleep(30)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="more verbose",
                        action="store_true")
    parser.add_argument("-r", "--replay-history", type=str,
                        help="replay history from a directory")
    parser.add_argument("-o", "--observers", type=str, help="observers")
    parser.add_argument("-m", "--markets", type=str, help="markets")
    args = parser.parse_args()
    level = logging.INFO
    if args.verbose:
        level = logging.DEBUG
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',
                        level=level)
    arbitrer = Arbitrer()
    if args.replay_history:
        if args.observers:
            arbitrer.init_observers(args.observers.split(","))
        if args.markets:
            arbitrer.init_markets(args.markets.split(","))
        arbitrer.replay_history(args.replay_history)
    else:
        arbitrer.loop()

if __name__ == '__main__':
    main()
