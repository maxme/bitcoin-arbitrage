from .observer import Observer
import json
import time
import os
from private_markets import haobtccny,huobicny,okcoincny
import sys
import traceback
import config
import logging

class BalanceDumper(Observer):
    exchange = 'HaobtcCNY'

    out_dir = 'balance_history/'

    def __init__(self):
        self.clients = {
            # TODO: move that to the config file
            "HaobtcCNY": haobtccny.PrivateHaobtcCNY(config.HAOBTC_API_KEY, config.HAOBTC_SECRET_TOKEN),
        }
        
        self.cny_balance = 0
        self.btc_balance = 0
        self.cny_frozen = 0
        self.btc_frozen = 0
        self.cny_total = 0
        self.btc_total = 0
       
        try:
            os.mkdir(self.out_dir)
        except:
            pass

    def update_trade_history(self, exchange, time, price, cny, btc):
        filename = self.out_dir + exchange + '_balance.csv'
        need_header = False

        if not os.path.exists(filename):
            need_header = True

        fp = open(filename, 'a+')

        if need_header:
            fp.write("timestamp, price, cny, btc\n")

        fp.write(("%d") % time +','+("%.2f") % price+','+("%.2f") % cny+','+ str(("%.4f") % btc) +'\n')
        fp.close()

    def update_balance(self):
        for kclient in self.clients:
            self.clients[kclient].get_info()
            self.cny_balance = self.clients[kclient].cny_balance
            self.btc_balance = self.clients[kclient].btc_balance
            
            self.cny_frozen = self.clients[kclient].cny_frozen
            self.btc_frozen = self.clients[kclient].btc_frozen

    def cny_balance_total(self, price):
        return self.cny_balance + self.cny_frozen+ (self.btc_balance + self.btc_frozen)* price
    
    def btc_balance_total(self, price):
        return self.btc_balance + self.btc_frozen  + (self.cny_balance +self.cny_frozen ) / (price*1.0)


    def begin_opportunity_finder(self, depths):
        # Update client balance
        self.update_balance()

        # get price
        try:
            bid_price = int(depths[self.exchange]["bids"][0]['price'])
            ask_price = int(depths[self.exchange]["asks"][0]['price'])
        except  Exception as ex:
            logging.warn("exception depths:%s" % ex)
            t,v,tb = sys.exc_info()
            print(t,v)
            traceback.print_exc()

            # logging.warn(depths)
            return

        if bid_price == 0 or ask_price == 0:
            logging.warn("exception ticker")
            return
        
        if abs(self.cny_total - self.cny_balance_total(bid_price)) > 3 or abs(self.btc_total - self.btc_balance_total(ask_price)) > 0.002:
            logging.info("update_balance-->")
            self.cny_total = self.cny_balance_total(bid_price)
            self.btc_total = self.btc_balance_total(ask_price)
            self.update_trade_history(self.exchange, time.time(), bid_price, self.cny_total, self.btc_total)

    def end_opportunity_finder(self):
        pass

    def opportunity(self, profit, volume, buyprice, kask, sellprice, kbid, perc, weighted_buyprice, weighted_sellprice):
        pass
