import json
import sys
# Enable websocket protocol debugging
import websocket
websocket._debug = True


def on_message(ws, message):
    print(message)


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("### closed ###")


def on_open(ws):
    def run(*args):
        for i in range(30000):
            time.sleep(1)
            ws.send("Hello %d" % i)
        time.sleep(1)
        ws.close()
        print("thread terminating...")
    thread.start_new_thread(run, ())

if __name__ == "__main__":

    ws = websocket.WebSocketApp("wss://websocket.mtgox.com/mtgox",
                                on_message,
                                on_error)
    ws.on_open = on_open

    ws.run_forever()
