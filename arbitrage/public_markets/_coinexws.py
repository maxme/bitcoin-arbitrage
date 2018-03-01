import json
import sys
import logging
import time
from arbitrage import config
from websocket import WebSocketApp
from threading import Thread
from arbitrage.public_markets.market import Market



class Coinex(Market):
    def __init__(self, currency, code, reverse_pair = False):
        super().__init__(currency)
        self.code = code
        self.reverse_pair = reverse_pair
        self.update_rate = 0.0001
        self.isWebsocket = True
        self.depth_data = {'asks':[],'bids':[]}
        self.depth_update_time = time.time()
        self.last_ping_time = time.time()
        self.host = "wss://socket.coinex.com/"

        self.ws = WebSocketApp(self.host,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close,
                on_open=self.on_open)

        self.work_thread = Thread(target=self._websocket_background_services)
        self.work_thread.daemon = True  
        self.work_thread.start() 

        self.need_reconnect = True
      

    def _websocket_background_services(self):
        self.ws.run_forever()

        while self.need_reconnect:
            time.sleep(1)
            logging.info("### coinex ws reconnect ###")
            self.ws.run_forever()


    def _update_list(self, tlist, olist):
        _olist_map = {}

        for item in olist:
            _olist_map[item[0]] = item[1]


        _ret_list = tlist

        _operated_price = []

        #must reverse traverse,cause we will delete and change 
        for i in range(len(_ret_list)-1,-1,-1):
            _price = _ret_list[i][0]
            if _price in _olist_map:
                _operated_price.append(_price)
                _value = _olist_map[_price] 
                if _value == '0':
                    #remove
                    _ret_list.remove(_ret_list[i])

                else:
                    #change value
                    _ret_list[i][1] = _value

        #rest is add operation
        for i in _olist_map:
            if i not in _operated_price:
                _value = _olist_map[i]
                if _value != '0':
                    _ret_list.append([i,_value])
        return _ret_list

    def _update_orderbook(self,change_data):
        _tmp_asks = self.depth_data['asks'][:]
        _tmp_bids = self.depth_data['bids'][:]

        if 'asks' in change_data:
            _tmp_asks = self._update_list(_tmp_asks,change_data['asks'])

        if 'bids' in change_data:
            _tmp_bids = self._update_list(_tmp_bids,change_data['bids'])


        self.depth_data = {'asks':_tmp_asks,'bids':_tmp_bids}
 

    def on_message(self, ws, message):
        data = json.loads(message)
        if 'params' in data:
            data = data['params']
            _b_full_orderbook = data[0]
            if _b_full_orderbook:
                 self.depth_data = data[1]
            else:
                self._update_orderbook(data[1])

            self.depth_update_time = time.time()
        elif 'result' in data:
            if data['result'] == 'pong':
                logging.verbose('get coinex pong message')
 


    def on_error(self, ws, error):
        logging.info("### coinex ws err: %s ###" % (str(error)))


    def on_close(self, ws):
        logging.info("### coinex ws closed ###")
        

    def on_open(self, ws):
        logging.info("### coinex ws opened ###")
        self.depth_update_time = time.time()
        jdata = {
              "method":"depth.subscribe",
              "params":[
                self.code.upper(),               #1.market: See<API invocation description·market> 
                50,                      #2.limit: Count limit
                "0"                     #3.interval: Merge，String
              ],
              "id":0
            }
        ws.send(json.dumps(jdata))
    def ping(self):
        self.last_ping_time = time.time()
        jdata = {
              "method":"server.ping",
              "params":[],
              "id":11
            }
        self.ws.send(json.dumps(jdata))

    def update_depth(self):
        _cur_time = time.time()
        timediff = _cur_time - self.depth_update_time
        if timediff > config.websocket_expiration_time:
            self.depth_data = {'asks':[],'bids':[]}
            raise Exception('get coinexws data timeout.')
        timediff = _cur_time - self.last_ping_time
        if timediff > 5:
            self.ping()

        self.depth = self.format_depth(self.depth_data)
        

    def sort_and_format(self, l, reverse):

        r = []

        if self.reverse_pair:
            for i in l:
                o_price = float(i[0])
                o_amount = float(i[1])

                d_price = 1.0 / o_price
                d_amount = o_amount * o_price

                r.append({'price': d_price, 'amount': d_amount})
        else:
            for i in l:
                r.append({'price': float(i[0]), 'amount': float(i[1])})

        r.sort(key=lambda x: float(x['price']), reverse=reverse)
        return r

    def format_depth(self, depth):
        if self.reverse_pair:
            asks = self.sort_and_format(depth['bids'], False)
            bids = self.sort_and_format(depth['asks'], True)
        else:
            bids = self.sort_and_format(depth['bids'], True)
            asks = self.sort_and_format(depth['asks'], False)  
        return {'asks': asks, 'bids': bids}

def test_update_depth():
    C = Coinex("BTC", "btcbch",True)

    while True:
        time.sleep(0.1)

    """
    try:

        while True:
            time.sleep(0.1)
            C.work_thread.join(2)
            if not C.work_thread.isAlive:
                break
    except KeyboardInterrupt:
        print("Ctrl-c pressed ...")
        C.need_reconnect = False
        C.ws.close()
        print('exiting....')
        """


