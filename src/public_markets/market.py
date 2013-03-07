import time

class Market(object):
    def __init__(self, currency):
        self.name = self.__class__.__name__
        self.currency = currency
        self.depth_updated = 0
        self.update_rate = 60

    def get_depth(self):
        timediff = time.time() - self.depth_updated
        if (timediff > self.update_rate):
            self.ask_update_depth()
        # FIXME: debug
        #self.depth = {"asks": self.depth["asks"][2:], "bids": self.depth["bids"][2:]}
        return self.depth

    def ask_update_depth(self):
        self.update_depth()
        self.depth_updated = time.time()

    def get_ticker(self):
        depth = self.get_depth()
        res = {'ask': depth['asks'][0],
               'bid': depth['bids'][0]}
        return res

    ## Abstract methods
    def update_depth(self):
        pass

    def buy(self, price, amount):
        pass

    def sell(self, price, amount):
        pass

