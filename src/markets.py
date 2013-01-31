#!/usr/bin/env python

import json
import urllib
import urllib2
import time
from pprint import pprint

MARKETS_URL = "http://bitcoincharts.com/t/markets.json"
BITCOIN_CENTRAL_URL = "https://bitcoin-central.net/ticker.json"
SAT=100000000.0

def get_markets():
    try:
        response = urllib2.urlopen(MARKETS_URL)
    except:
        print "error getting markets from bitcoincharts"
        return ""
    res = response.read() # json_response = json.loads(response.read())
    return res

def get_bitcoincentral():
    try:
        response = urllib2.urlopen(BITCOIN_CENTRAL_URL)
    except:
        print "error getting markets from bitcoincentral"
        return ""
    res = response.read() # json_response = json.loads(response.read())
    return res

def inject_bitcoincentral(json_data, out):
    res = { "symbol": "bc2EUR" }
    if not json_data:
        return res
    data = json.loads(json_data)
    res["ask"] = data["ask"]
    res["bid"] = data["bid"]
    res["high"] = data["high"]
    res["low"] = data["low"]
    res["volume"] = data["volume"]
    res["currency"] = "EUR"
    out.append(res)
    return res

def format_symbols(data):
    res = ""
    for i in data:
        res += "%s: %.4f/%.4f - " % (i["symbol"], i["bid"], i["ask"])
    return res

def get_all_markets():
    json_data = get_markets()
    if not json_data:
        return []
    try:
        data = json.loads(json_data)
    except:
        print "error in json:", json_data
        return []
    inject_bitcoincentral(get_bitcoincentral(), data)
    return data

def check_arbitrage_opportunity(json_data):
    if not json_data:
        return []
    try:
        data = json.loads(json_data)
    except:
        print "error in json:", json_data
        return []
    inject_bitcoincentral(get_bitcoincentral(), data)
    filtered = []
    res = []
    for i in data:
        #if i["currency"] == "EUR":
        #    print i["symbol"]
        if i["symbol"] in ["mtgoxEUR", "intrsngEUR", "bc2EUR"]:
            filtered.append(i)
    print "ticker " + format_symbols(filtered)
    for i in filtered:
        for j in filtered:
            if i == j:
                continue
            try:
                if float(i["ask"]) < float(j["bid"]):
                    perc = (j["bid"] - i["ask"]) / j["bid"] * 100
                    res.append([i["ask"], i["symbol"], j["bid"], j["symbol"], perc])
                    print time.strftime("%d/%m/%Y %H:%M:%S") + " - opportunity - buy at %.4f (%s) and sell at %.4f (%s) - %.4f%%" % (i["ask"], i["symbol"], j["bid"], j["symbol"], perc)
            except Exception, e:
                print e
                continue
    return res

def watch_for_good_op(good_perc, callback, sleep_time=120):
    while True:
        res = check_arbitrage_opportunity(get_markets())
        for i in res:
            if i[4] > good_perc:
                callback("[Arbitrage-bot] Opportunity - buy at %.4f (%s) and sell at %.4f (%s) - %.4f%%" % (i[0], i[1], i[2], i[3], i[4]), "", i)
        time.sleep(sleep_time)
