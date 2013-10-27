from decimal import Decimal

class Trade(object):
    def __init__(self, market_name, type, price):
        self.market_name = market_name
        self.type = type
        self.price = price

    def trade_from(self, volume, currency):
        self.from_volume = volume
        self.from_currency = currency
        return self

    def trade_to(self, volume, currency):
        self.to_volume = volume
        self.to_currency = currency
        return self

    def __str__(self):
        if self.type == "buy":
            return "buy %f %s at %.4f %s on %s with %f %s" % (
                self.to_volume, self.to_currency, self.price,
                self.from_currency, self.market_name,
                self.from_volume, self.from_currency
            )
        else:
            return "sell %f %s at %.4f %s on %s for %f %s" % (
                self.from_volume, self.from_currency, self.price,
                self.to_currency, self.market_name,
                self.to_volume, self.to_currency
            )
