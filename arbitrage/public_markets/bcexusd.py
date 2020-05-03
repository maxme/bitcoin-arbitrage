from arbitrage.public_markets._bcex import Bcex
from time import sleep

class BcexUSD(Bcex):
    def __init__(self):
        super().__init__("USD", "BTC-USD")


if __name__ == "__main__":
    market = BcexUSD()
    while True:
        sleep(2)
        market.update_depth()
        print(market.get_ticker())