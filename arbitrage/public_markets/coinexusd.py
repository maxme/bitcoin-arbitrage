from arbitrage.public_markets._coinex import Coinex

class CoinexUSD(Coinex):
    def __init__(self):
        super().__init__("USD", "btcusdt")

if __name__ == "__main__":
    market = CoinexUSD()
    market.update_depth()
    print(market.get_ticker())
