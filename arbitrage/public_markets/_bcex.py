from bcex.core.bcex_interface import BcexInterface
from bcex.core.websocket_client import Environment, Channel
from arbitrage.public_markets.market import Market


class Bcex(Market):
    ORDER_BOOK_DEPTH = 10
    def __init__(self, currency, code):
        super().__init__(currency)
        self.code = code
        self.update_rate = 30
        self._client = BcexInterface(symbols=[code],env=Environment.PROD, channels=[Channel.L2])
        self._client.connect()

    def update_depth(self):
        ob = self._client.get_order_book(self.code)
        self.depth = self.format_depth(ob)  #KEY IS PRICE VALUE IS AMOUNT SORTED LOW TO HIGH

    def sort_and_format(self, l, reverse=False):
        r = []
        for i in range(self.ORDER_BOOK_DEPTH):
            if not reverse:
                if len(l) >= i:
                    item = l.peekitem(i)
                    r.append({"price": float(item[0]), "amount": float(item[1])})
            else:
                if len(l) >= i:
                    item = l.peekitem(-(i+1))
                    r.append({"price": float(item[0]), "amount": float(item[1])})
        return r

    def format_depth(self, depth):
        bids = self.sort_and_format(depth["bids"], True)
        asks = self.sort_and_format(depth["asks"], False)
        return {"asks": asks, "bids": bids}