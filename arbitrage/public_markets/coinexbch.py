from arbitrage.public_markets._coinexws import Coinex

class CoinexBCH(Coinex):
    def __init__(self):
        super().__init__("BTC", "btcbch",True)

if __name__ == "__main__":
    market = CoinexBCH()
    market.update_depth()
    print(market.get_ticker())
