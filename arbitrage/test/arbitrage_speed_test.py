import sys
sys.path.append('../../')
import json
import arbitrage
import time
from arbitrage.observers import observer
from arbitrage.arbitrer import Arbitrer


class TestObserver(observer.Observer):
    def opportunity(self, profit, volume, buyprice, kask, sellprice, kbid,
                    perc, weighted_buyprice, weighted_sellprice):
        print("profit: %.3f" % profit)

def main():
    arbitrer = Arbitrer()
    depths = arbitrer.depths = json.load(open("speed-test.json"))
    print('start test')
    start_time = time.time()
    testobs = TestObserver()
    arbitrer.observers = [testobs]
    arbitrer.arbitrage_opportunity("BitstampUSD", depths["BitstampUSD"]["asks"][0],
                                   "KrakenEUR", depths["KrakenEUR"]["asks"][0])
    print('end test')
    # FIXME: add asserts
    elapsed = time.time() - start_time
    print("Time: %.3f" % elapsed)


if __name__ == '__main__':
    main()
