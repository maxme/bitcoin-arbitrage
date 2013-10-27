class Trade(object):
    def __init__(self, market_name):
        self.market_name = market_name

    def trade_from(self, volume, currency):
        self.from_volume = volume
        self.from_currency = currency
        return self

    def trade_to(self, volume, currency):
        self.to_volume = volume
        self.to_currency = currency
        return self
