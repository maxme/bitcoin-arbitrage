import json
import sys
import pysher
from arbitrage.public_markets.market import Market
import logging
import time
from arbitrage import config

class Bitstamp(Market):
    def __init__(self, currency, code):
        super().__init__(currency)
        self.code = code
        self.update_rate = 0.0001
        self.isWebsocket = True
        self.pusher = pysher.Pusher("de504dc5763aeef9ff52",log_level=logging.ERROR)
        self.pusher.connection.bind('pusher:connection_established', self.connect_handler)
        self.pusher.connect()
        self.depth_data = {'asks':[],'bids':[]}
        self.depth_update_time = time.time()

    def channel_callback(self, data):
        self.depth_data = json.loads(data)
        self.depth_update_time = time.time()

    def connect_handler(self, data):
        logging.info("### bitstamp ws opened ###")
        channel_name = "order_book_"+self.code

        self.channel = self.pusher.subscribe(channel_name)

        self.channel.bind('data', self.channel_callback)



    def update_depth(self):
        timediff = time.time() - self.depth_update_time
        if timediff > config.websocket_expiration_time:
            self.depth_data = {'asks':[],'bids':[]}
            raise Exception('get bitstampws data timeout.')

        self.depth = self.format_depth(self.depth_data)
        

    def sort_and_format(self, l, reverse):
        r = []
        for i in l:
            r.append({'price': float(i[0]), 'amount': float(i[1])})
        r.sort(key=lambda x: float(x['price']), reverse=reverse)
        return r

    def format_depth(self, depth):
        bids = self.sort_and_format(depth['bids'], True)
        asks = self.sort_and_format(depth['asks'], False)
        return {'asks': asks, 'bids': bids}

def test_update_depth():
    import time
    b = Bitstamp("BTC", "bchbtc")


    while True:
        time.sleep(1)
        b.update_depth()