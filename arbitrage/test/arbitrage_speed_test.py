import json
import time
from arbitrage.observers import observer
from arbitrage import arbiter


class TestObserver(observer.Observer):
    def opportunity(self, profit, volume, buyprice, kask, sellprice, kbid,
                    perc, weighted_buyprice, weighted_sellprice):
        print("Time: %.3f" % profit)


def main():
    a = arbiter.Arbiter()
    depths = a.depths = json.load(open("speed-test.json"))
    start_time = time.time()
    testobs = TestObserver()
    a.observers = [testobs]
    a.arbitrage_opportunity("BitstampUSD", depths["BitstampUSD"]["asks"][0],
                                   "MtGoxEUR", depths["MtGoxEUR"]["asks"][0])
    # FIXME: add asserts
    elapsed = time.time() - start_time
    print("Time: %.3f" % elapsed)


if __name__ == '__main__':
    main()
