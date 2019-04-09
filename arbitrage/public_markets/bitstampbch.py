from arbitrage.public_markets._bitstampws import Bitstamp

class BitstampBCH(Bitstamp):
    def __init__(self):
        super().__init__("BTC", "bchbtc")

if __name__ == "__main__":
    market = BitstampBCH()
    market.update_depth()
    print(market.get_ticker())
