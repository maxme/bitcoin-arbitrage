# Copyright (C) 2013, Maxime Biais <maxime@biais.org>

from .mtgox import PrivateMtGox


class PrivateMtGoxEUR(PrivateMtGox):
    def __init__(self):
        super().__init__()
        self.ticker_url = {"method": "GET", "url":
                           "https://mtgox.com/api/1/BTCEUR/public/ticker"}
        self.buy_url = {"method": "POST", "url":
                        "https://mtgox.com/api/1/BTCEUR/private/order/add"}
        self.sell_url = {"method": "POST", "url":
                         "https://mtgox.com/api/1/BTCEUR/private/order/add"}
        self.currency = "EUR"

    def get_info(self):
        params = [("nonce", self._create_nonce())]
        response = self._send_request(self.info_url, params)
        if response and "result" in response and response["result"] == "success":
            self.btc_balance = self._from_int_amount(int(
                response["return"]["Wallets"]["BTC"]["Balance"]["value_int"]))
            self.eur_balance = self._from_int_price(int(
                response["return"]["Wallets"]["EUR"]["Balance"]["value_int"]))
            self.usd_balance = self.fc.convert(self.eur_balance, "EUR", "USD")
            return 1
        return None
