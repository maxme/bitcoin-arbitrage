
class TradeException(Exception):
    pass

class Market(object):
    def __init__(self):
        self.name = self.__class__.__name__
        self.btc_balance = 0.
        self.eur_balance = 0.
        self.usd_balance = 0.

    def __str__(self):
        return "%s: %s" % (self.name, str({"btc_balance": self.btc_balance,
                                           "eur_balance": self.eur_balance,
                                           "usd_balance": self.usd_balance}))

    ## Abstract methods
    def buy(self, price, amount):
        pass

    def sell(self, price, amount):
        pass

    def deposit(self):
        pass

    def withdraw(self, amount, address):
        pass

    def get_info(self):
        pass
