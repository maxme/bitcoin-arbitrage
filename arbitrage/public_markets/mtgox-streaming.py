import websocket    # https://github.com/liris/websocket-client/tree/py3
import threading


def on_message(ws, message):
    print(message)


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("### closed ###")


def run(*args):
    command = '{"op": "mtgox.subscribe", "type": "depth"}'
    ws.send(command.encode('utf-8'))


def on_open(ws):
    threading.Thread(target=run).start()


if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://websocket.mtgox.com/mtgox",
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.run_forever()


