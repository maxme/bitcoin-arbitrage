import public_markets
import observers
import config
import time
import logging
import json

class Arbitrer:
    def __init__(self):
        self.markets = []
        self.observers = []
        self.depths = {}
        for market_name in config.markets:
            exec('import public_markets.' + market_name.lower())
            market =  eval('public_markets.' + market_name.lower() + '.' + market_name + '()')
            self.markets.append(market)
        for observer_name in config.observers:
            exec('import observers.' + observer_name.lower())
            observer =  eval('observers.' + observer_name.lower() + '.' + observer_name + '()')
            self.observers.append(observer)

    def get_profit_for(self, mi, mj, kask, kbid):
        if self.depths[kask]["asks"][mi]["price"] >= self.depths[kbid]["bids"][mj]["price"]:
            return 0, 0

        max_amount_buy = 0
        for i in range(mi + 1):
            max_amount_buy += self.depths[kask]["asks"][i]["amount"]
        max_amount_sell = 0
        for j in range(mj + 1):
            max_amount_sell += self.depths[kbid]["bids"][j]["amount"]
        max_amount = min(max_amount_buy, max_amount_sell)

        buy_total = 0
        w_buyprice = 0
        for i in range(mi + 1):
            price = self.depths[kask]["asks"][i]["price"]
            amount = min(max_amount, buy_total + self.depths[kask]["asks"][i]["amount"]) - buy_total
            if amount <= 0:
                break
            buy_total += amount
            if w_buyprice == 0:
                w_buyprice = price
            else:
                w_buyprice = (w_buyprice * (buy_total - amount) + price * amount) / buy_total

        sell_total = 0
        w_sellprice = 0
        for j in range(mj + 1):
            price = self.depths[kbid]["bids"][j]["price"]
            amount = min(max_amount, sell_total + self.depths[kbid]["bids"][j]["amount"]) - sell_total
            if amount < 0:
                break
            sell_total += amount
            if w_sellprice == 0:
                w_sellprice = price
            else:
                w_sellprice = (w_sellprice * (sell_total - amount) + price * amount) / sell_total

        profit = sell_total * w_sellprice - buy_total * w_buyprice
        return profit, sell_total

    def get_max_depth(self, kask, kbid):
        i = 0
        j = 0
        while self.depths[kask]["asks"][i]["price"] < self.depths[kbid]["bids"][0]["price"]:
            i += 1
        while self.depths[kask]["asks"][0]["price"] < self.depths[kbid]["bids"][j]["price"]:
            j += 1
        return i, j

    def arbitrage_depth_opportunity(self, kask, kbid):
        maxi, maxj = self.get_max_depth(kask, kbid)
        best_profit = 0
        best_i, best_j = (0, 0)
        best_volume = 0
        for i in range(maxi + 1):
            for j in range(maxj + 1):
                profit, volume = self.get_profit_for(i, j, kask, kbid)
                if profit >= 0 and profit >= best_profit:
                    best_profit = profit
                    best_volume = volume
                    best_i, best_j = (i, j)
        return best_profit, best_volume, self.depths[kask]["asks"][best_i]["price"],\
               self.depths[kbid]["bids"][best_j]["price"]

    def arbitrage_opportunity(self, kask, ask, kbid, bid):
        perc = (bid["price"] - ask["price"]) / bid["price"] * 100
        profit, volume, buyprice, sellprice = self.arbitrage_depth_opportunity(kask, kbid)
        logging.debug("buy at %.4f (%s) and sell at %.4f (%s) - %.4f%%" % (ask["price"], kask, bid["price"], kbid, perc))
        perc2 = (1 - (volume - (profit/buyprice)) / volume) * 100
        for observer in self.observers:
            observer.opportunity(profit, volume, buyprice, kask, sellprice, kbid, perc2)


    def update_depths(self):
        self.depths = {}
        for market in self.markets:
            self.depths[market.name] = market.get_depth()

    def tickers(self):
        for market in self.markets:
            logging.info("ticker: " + market.name + " - " + str(market.get_ticker()))

    def loop(self):
        while True:
            self.update_depths()
            self.tickers()
            for kmarket1 in self.depths:
                for kmarket2 in self.depths:
                    if kmarket1 == kmarket2: # same market
                        continue
                    market1 = self.depths[kmarket1]
                    market2 = self.depths[kmarket2]
                    if float(market1["asks"][0]['price']) < float(market2["bids"][0]['price']):
                        self.arbitrage_opportunity(kmarket1, market1["asks"][0], kmarket2, market2["bids"][0])
            time.sleep(30)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logging.INFO)
    arbitrer = Arbitrer()
    arbitrer.loop()
