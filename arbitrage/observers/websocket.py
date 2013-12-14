import config
import json
import logging
import threading
from .observer import Observer
from .traderbot import order_placed, tradechain_executed

try:
    import tornado.ioloop
    import tornado.web
    from tornado import websocket

except ImportError:
    tornado = False
    logging.warn("Could not load 'tornado'. WebSocket observer disabled!")

GLOBALS={
    'opportunity_sockets': [],
    'traderbot_sockets': [],
    'log_sockets': [],
    'socket_singleton': None,
    'tornado_loaded': tornado != False
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


class LogSocket(websocket.WebSocketHandler):
    def open(self):
        GLOBALS["log_sockets"].append(self)
        logging.info("[WebSocket] Log client connected.") 

    def on_close(self):
        GLOBALS["log_sockets"].remove(self)
        logging.info("[WebSocket] Log client disconnected.") 


class LogSocketHandler(logging.Handler):
    def emit(self, record):
        for socket in GLOBALS['log_sockets']:
            socket.write_message(self.format(record))


class _WebSocket(Observer):
    def __init__(self):
        self.application = tornado.web.Application([
            (r"/", OpportunitySocket),
            (r"/traderbot", TraderBotSocket),
            (r"/log", LogSocket)
        ])

        port = config.ws_port if hasattr(config, "ws_port") else 8888
        logging.info("[WebSocket] Serving trade updates on port %i" % port)
        logging.getLogger().addHandler(LogSocketHandler())
        self.application.listen(port)
        self.thread = threading.Thread(target = tornado.ioloop.IOLoop.instance().start)
        self.thread.daemon = True
        self.thread.start()

    def opportunity(self, tradechains):
        best_chain = sorted(tradechains, key=lambda x: x.profit)[-1]
        for socket in GLOBALS['opportunity_sockets']:
            socket.write_message(json.dumps(best_chain.__dict__))

    def shutdown(self):
        tornado.ioloop.IOLoop.instance().stop()
        GLOBALS["socket_singleton"] = None


class _MockWebSocket(object):
    """ Simplifies disabling the WebSocket observer. """

    def opportunity(*args, **kwargs):
        pass

    def shutdown(*args, **kwargs):
        GLOBALS["socket_singleton"] = None


def WebSocket():
    ws_class = _WebSocket

    if not GLOBALS["tornado_loaded"]:
        ws_class = _MockWebSocket

    if not GLOBALS["socket_singleton"]:
        GLOBALS["socket_singleton"] = ws_class()

    return GLOBALS["socket_singleton"]

# Signals

def write_traderbot_trade(trade):
    for socket in GLOBALS['traderbot_sockets']:
        socket.write_message(json.dumps({"trade": trade.__dict__}))


def write_traderbot_tradechain(tradechain):
    for socket in GLOBALS['traderbot_sockets']:
        socket.write_message(json.dumps({"tradechain": tradechain.__dict__}))

order_placed.connect(write_traderbot_trade)
tradechain_executed.connect(write_traderbot_tradechain)
