class Market(object):
    def __init__(self):
        self.name = self.__class__.__name__
        self.btc_balance = 0
        self.eur_balance = 0

    ## Abstract methods
    def buy(self, price, amount):
        pass

    def sell(self, price, amount):
        pass

    def get_info(self):
        pass
