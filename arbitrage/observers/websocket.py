import config
import logging
import threading
import tornado.ioloop
import tornado.web
from tornado import websocket
from .observer import Observer

GLOBALS={
    'sockets': []
}

class ClientSocket(websocket.WebSocketHandler):
    def open(self):
        GLOBALS['sockets'].append(self)
        logging.info("[WebSocket] Client connected.") 

    def on_close(self):
        GLOBALS['sockets'].remove(self)
        logging.info("[WebSocket] Client disconnected.") 

class WebSocket(Observer):
    def opportunity(self, tradechains):
        best_chain = sorted(tradechains, key=lambda x: x.profit)[-1]
        for socket in GLOBALS['sockets']:
            socket.write_message(str(best_chain))

application = tornado.web.Application([
    (r"/", ClientSocket)
])

port = config.ws_port if hasattr(config, "ws_port") else 8888
logging.info("[WebSocket] Serving trade updates on port %i" % port) 
application.listen(port)
thread = threading.Thread(target = tornado.ioloop.IOLoop.instance().start)
thread.daemon = True
thread.start()
