import config
import json
import logging
import threading
import tornado.ioloop
import tornado.web
from tornado import websocket
from .observer import Observer
from .traderbot import order_placed

GLOBALS={
    'opportunity_sockets': [],
    'traderbot_sockets': []
}


class OpportunitySocket(websocket.WebSocketHandler):
    def open(self):
        GLOBALS["opportunity_sockets"].append(self)
        logging.info("[WebSocket] Client connected.") 

    def on_close(self):
        GLOBALS["opportunity_sockets"].remove(self)
        logging.info("[WebSocket] Client disconnected.") 


class TraderBotSocket(websocket.WebSocketHandler):
    def open(self):
        GLOBALS["traderbot_sockets"].append(self)
        logging.info("[WebSocket] TraderBot client connected.") 

    def on_close(self):
        GLOBALS["traderbot_sockets"].remove(self)
        logging.info("[WebSocket] TraderBot client disconnected.") 


class WebSocket(Observer):
    def opportunity(self, tradechains):
        best_chain = sorted(tradechains, key=lambda x: x.profit)[-1]
        for socket in GLOBALS['opportunity_sockets']:
            socket.write_message(json.dumps(best_chain.__dict__))


def write_traderbot_trades(trade):
    for socket in GLOBALS['traderbot_sockets']:
        socket.write_message(json.dumps(trade.__dict__))


application = tornado.web.Application([
    (r"/", OpportunitySocket),
    (r"/traderbot", TraderBotSocket)
])

port = config.ws_port if hasattr(config, "ws_port") else 8888
logging.info("[WebSocket] Serving trade updates on port %i" % port) 
application.listen(port)
thread = threading.Thread(target = tornado.ioloop.IOLoop.instance().start)
thread.daemon = True
thread.start()
order_placed.connect(write_traderbot_trades)
