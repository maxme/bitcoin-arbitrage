# Copyright (C) 2013, Maxime Biais <maxime@biais.org>

from .mtgox import PrivateMtGox


class PrivateMtGoxUSD(PrivateMtGox):
    def __init__(self):
        super().__init__()
        self.ticker_url = {"method": "GET", "url":
                           "https://mtgox.com/api/1/BTCUSD/public/ticker"}
        self.buy_url = {"method": "POST", "url":
                        "https://mtgox.com/api/1/BTCUSD/private/order/add"}
        self.sell_url = {"method": "POST", "url":
                         "https://mtgox.com/api/1/BTCUSD/private/order/add"}
        self.currency = "USD"

    def get_info(self):
        params = [("nonce", self._create_nonce())]
        response = self._send_request(self.info_url, params)
        if response and "result" in response and response["result"] == "success":
            self.btc_balance = self._from_int_amount(int(
                response["return"]["Wallets"]["BTC"]["Balance"]["value_int"]))
            self.usd_balance = self._from_int_price(int(
                response["return"]["Wallets"]["USD"]["Balance"]["value_int"]))
            return 1
        return None
