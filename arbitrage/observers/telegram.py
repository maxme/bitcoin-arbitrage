import logging
from arbitrage.observers.observer import Observer
from arbitrage import config
import urllib.request
import urllib.error
import urllib.parse
import json
import time


repeat_count = 0
prev_message = ''

def send_message(message):

    max_retry = 10
    retry = 0
    while retry < max_retry:
        try:
            _send_message(message)
            print('retry times',retry)
        except Exception as e:
            print('send_message occur exception!')
            time.sleep(20)
            retry = retry+1
            continue
        break


def _send_message(message):
    global prev_message,repeat_count
    if message == prev_message:
        repeat_count += 1
        if repeat_count >= config.telegram_rmsc:
            return
    else:
        repeat_count = 0

    url = ("https://api.telegram.org/bot%s/sendMessage?chat_id=%s&text=%s" 
            % (config.telegram_token, config.telegram_chatid, urllib.parse.quote_plus(message)))

    req = urllib.request.Request(url, None, headers={
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "*/*",
        "User-Agent": "curl/7.24.0 (x86_64-apple-darwin12.0)"})
    res = urllib.request.urlopen(req)
    #retrun_data = json.loads(res.read().decode('utf8'))

    prev_message = message



class Telegram(Observer):
    def opportunity(self, profit, volume, buyprice, kask, sellprice, kbid, perc,
                    weighted_buyprice, weighted_sellprice):
        if profit > config.profit_thresh and perc > config.perc_thresh:
            pair_names = str.split(config.pair, "_")
            pair1_name = str.upper(pair_names[0])
            pair2_name = str.upper(pair_names[1])
            message = "profit: %f %s with volume: %f %s - buy from %s sell to %s ~%.2f%%" \
                % (profit, pair2_name, volume, pair1_name, kask, kbid, perc)
            send_message(message)