from .market import Market
import urllib.parse
import urllib.error
import urllib.request
import json
import logging
import config


class PrivateRipple(Market):
    def __init__(self):
        super().__init__()
        self.private_rippled_url = config.ripple_private_rippled
        self.public_rippled_url = config.ripple_rippled
        self.address = config.ripple_useraddress
        self.secret = config.ripple_usersecret
        self.btc_issuer = config.ripple_BTC_issuer
        self.other_issuer = ""  # gets set by the child class
        self.get_info()

    def _buy(self, amount, price):
        buydata = ('{ "method" : "submit", '
            '"params" : [ { "secret" : "' + self.secret +
            '" }, { "tx_json" : { "TransactionType" : "OfferCreate", '
            '"Account" : "' + self.address + '", '
            '"TakerPays" : { "currency" : "BTC", '
            '"value" : "' + amount + '", '
            '"issuer" : "' + self.btc_issuer + '" }, '
            '"TakerGets" : { "currency" : "' + self.currency + '", '
            '"value" : "' + amount * price + '", '
            '"issuer" : "' + self.other_issuer + '" } } } ] }')
        buydata = infodata.encode('ascii')
        buyreq = urllib.request.Request(
            private_rippled_url,  # secret MUST stay secret!
            buydata,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "*/*",
                "User-Agent": "curl/7.24.0 (x86_64-apple-darwin12.0)"})
        buyres = urllib.request.urlopen(buyreq)
        # TODO: return None on error
        # TODO: make sure that the transaction actually took place
        answer = json.loads(buyres.read().decode('utf8'))
        print(answer)
        return "success"

    def _sell(self, amount, price):
        selldata = ('{ "method" : "submit", '
            '"params" : [ { "secret" : "' + self.secret +
            '" }, { "tx_json" : { "TransactionType" : "OfferCreate", '
            '"Account" : "' + self.address + '", '
            '"TakerPays" : { "currency" : "' + self.currency + '", '
            '"value" : "' + amount * price + '", '
            '"issuer" : "' + self.other_issuer + '" }, '
            '"TakerGets" : { "currency" : "BTC", '
            '"value" : "' + amount + '", '
            '"issuer" : "' + self.btc_issuer + '" } } } ] }')
        selldata = infodata.encode('ascii')
        sellreq = urllib.request.Request(
            private_rippled_url,  # secret MUST stay secret!
            selldata,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "*/*",
                "User-Agent": "curl/7.24.0 (x86_64-apple-darwin12.0)"})
        sellres = urllib.request.urlopen(sellreq)
        # TODO: return None on error
        # TODO: make sure that the transaction actually took place
        answer = json.loads(sellres.read().decode('utf8'))
        print(answer)
        return "success"

    def withdraw(self, amount, address):
        # TODO: implement
        return None

    def deposit(self):
        # TODO: implement
        return None
        
    def get_info(self):
        infodata = ('{ "method" : "account_lines", '
            '"params" : [ { "account" : "' + self.address + '" } ] }')
        infodata = infodata.encode('ascii')
        inforeq = urllib.request.Request(
            public_rippled_url,  # account data is public in Ripple
            infodata,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "*/*",
                "User-Agent": "curl/7.24.0 (x86_64-apple-darwin12.0)"})
        infores = urllib.request.urlopen(inforeq)
        # TODO: return None on error
        information = json.loads(infores.read().decode('utf8'))
        for trustline in information['result']['lines']:
        # TODO: handling of advanced account_line stuff e.g. quality_in/out
            if trustline['account'] == config.ripple_BTC_issuer:
                if trustline['currency'] == "BTC":
                    self.btc_balance = float(trustline['balance'])
            if trustline['account'] == config.ripple_USD_issuer:
                if trustline['currency'] == "USD":
                    self.usd_balance = float(trustline['balance'])
            if trustline['account'] == config.ripple_EUR_issuer:
                if trustline['currency'] == "EUR":
                    self.eur_balance = float(trustline['balance'])
        return 1
