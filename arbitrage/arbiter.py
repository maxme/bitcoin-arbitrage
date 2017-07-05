import logging

from arbitrage import registry
from concurrent.futures import ThreadPoolExecutor, wait

from arbitrage.config import Configuration

LOG = logging.getLogger(__name__)


class Arbiter(object):
    """Fetching depths from markets and calculate arbitrage opportunity"""

    def __init__(self, config: Configuration,
                 markets=None,
                 observers=None,
                 workers=10):

        self.config = config
        self.markets = markets or self.init_markets()
        self.observers = observers or self.init_observers()
        self.depths = {}
        self.thread_pool = ThreadPoolExecutor(max_workers=workers)
        self.market_names = []
        self.observer_names = []

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
        max_amount = min(max_amount_buy,
                         max_amount_sell,
                         self.config.max_tx_volume)

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
                w_sellprice = (w_sellprice * (
                    sell_total - amount) + price * amount) / sell_total

        profit = sell_total * w_sellprice - buy_total * w_buyprice
        return profit, sell_total, w_buyprice, w_sellprice

    def get_max_depth(self, kask, kbid):

        i, j = 0, 0

        bids = self.depths[kbid]["bids"]
        asks = self.depths[kask]["asks"]

        if not bids or not asks:
            return i, j

        while asks[i]["price"] < bids[0]["price"]:
            if i >= len(asks) - 1:
                break
            i += 1

        while asks[0]["price"] < bids[j]["price"]:
            if j >= len(bids) - 1:
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

    def arbitrage_opportunity(self, kask, ask, kbid, bid):
        perc = (bid["price"] - ask["price"]) / bid["price"] * 100
        profit, volume, buyprice, sellprice, weighted_buyprice, \
        weighted_sellprice = self.arbitrage_depth_opportunity(kask, kbid)
        if volume == 0 or buyprice == 0:
            return
        perc2 = (1 - (volume - (profit / buyprice)) / volume) * 100
        for observer in self.observers:
            observer.opportunity(
                profit, volume, buyprice, kask, sellprice, kbid,
                perc2, weighted_buyprice, weighted_sellprice)

    def __get_market_depth(self, market, depths):
        depths[market.name] = market.get_depth()

    def update_depths(self):
        depths = {}
        futures = []
        for market in self.markets:
            futures.append(self.thread_pool.submit(self.__get_market_depth,
                                                   market, depths))
        wait(futures, timeout=self.config.refresh_rate)
        return depths

    def tickers(self):
        for market in self.markets:
            ticker = market.get_ticker()
            msg = "ticker: %s - %s " % (market.name, str(ticker))
            LOG.debug(msg)

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
                        and len(market1["asks"]) > 0 and len(
                    market2["bids"]) > 0:
                    if float(market1["asks"][0]['price']) \
                            < float(market2["bids"][0]['price']):
                        self.arbitrage_opportunity(kmarket1,
                                                   market1["asks"][0],
                                                   kmarket2,
                                                   market2["bids"][0])

        for observer in self.observers:
            observer.end_opportunity_finder()

    def init_observers(self):
        result = []
        for name in self.config.observers:
            klass = registry.observers_registry.get(name, None)
            if not klass:
                LOG.error('The %s observer class does not exist', name)
            else:
                LOG.debug('The %s observer was initialized', name)
                result.append(klass(self.config))
        return result

    def init_markets(self):
        result = []
        for name in self.config.markets:
            klass = registry.markets_registry.get(name, None)
            if not klass:
                LOG.error('The %s market class does not exist', name)
            else:
                LOG.debug('The %s market was initialized', name)
                result.append(klass(self.config))
        return result
