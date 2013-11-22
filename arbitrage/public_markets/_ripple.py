import urllib.request
import urllib.error
import urllib.parse
import json
from .market import Market
import config


class Ripple(Market):
    def __init__(self, currency, code):
        super().__init__(currency)
        self.code = code  # the counter currency issuer to BTC
        self.update_rate = 20

    def update_depth(self):
        url = config.ripple_rippled
        biddata = ('{ "method" : "book_offers", '
                   '"params" : [ { "taker_pays" : '
                   '{ "currency" : "BTC", "issuer" : "' +
                   config.ripple_BTC_issuer +
                   '" }, "taker_gets" : '
                   '{ "currency" : "' +
                   self.currency +
                   '", "issuer" : "' +
                   self.code + '" } } ] }')
        biddata = biddata.encode('ascii')
        bidreq = urllib.request.Request(
            url,
            biddata,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "*/*",
                "User-Agent": "curl/7.24.0 (x86_64-apple-darwin12.0)"})
        bidres = urllib.request.urlopen(bidreq)
        biddepth = json.loads(bidres.read().decode('utf8'))

        askdata = ('{ "method" : "book_offers", '
                   '"params" : [ { "taker_gets" : '
                   '{ "currency" : "BTC", "issuer" : "' +
                   config.ripple_BTC_issuer +
                   '" }, "taker_pays" : '
                   '{ "currency" : "' +
                   self.currency +
                   '", "issuer" : "' +
                   self.code + '" } } ] }')
        askdata = askdata.encode('ascii')
        askreq = urllib.request.Request(
            url,
            askdata,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "*/*",
                "User-Agent": "curl/7.24.0 (x86_64-apple-darwin12.0)"})
        askres = urllib.request.urlopen(askreq)
        askdepth = json.loads(askres.read().decode('utf8'))

        self.depth = self.format_depth(biddepth, askdepth)

    def sort_and_format(self, l, reverse=False):
        l.sort(key=lambda x: float(x[0]), reverse=reverse)
        r = []
        for i in l:
            r.append({'price': float(i[0]), 'amount': float(i[1])})
        return r

    def format_depth(self, biddepth, askdepth):
        bids = []
        for bid in biddepth['result']['offers']:
            takerpays = bid['TakerPays']['value']
            takergets = bid['TakerGets']['value']
            if 'taker_pays_funded' in bid:
                takerpays = bid['taker_pays_funded']['value']
            if 'taker_gets_funded' in bid:
                takergets = bid['taker_gets_funded']['value']
            takerpays = float(takerpays)
            takergets = float(takergets)
            rate = takergets / takerpays
            bids.append([rate, takerpays])
        bids = self.sort_and_format(bids, True)

        asks = []
        for ask in askdepth['result']['offers']:
            takerpays = ask['TakerPays']['value']
            takergets = ask['TakerGets']['value']
            if 'taker_pays_funded' in ask:
                takerpays = ask['taker_pays_funded']['value']
            if 'taker_gets_funded' in ask:
                takergets = ask['taker_gets_funded']['value']
            takerpays = float(takerpays)
            takergets = float(takergets)
            rate = takerpays / takergets
            asks.append([rate, takergets])
        asks = self.sort_and_format(asks, False)
        return {'asks': asks, 'bids': bids}
