import logging
from .observer import Observer
import json
import time
import os
import math
import os, time
import sys
import traceback
import config
from private_markets import haobtccny, brokercny
from .marketmaker import MarketMaker

class HedgerBot(MarketMaker):
    exchange = 'HaobtcCNY'
    hedger = 'BrokerCNY'
    out_dir = 'hedger_history/'
    filename = exchange + '-bot.csv'

    def __init__(self):
        super().__init__()

        self.clients = {
            "HaobtcCNY": haobtccny.PrivateHaobtcCNY(config.HAOBTC_API_KEY, config.HAOBTC_SECRET_TOKEN),
            "BrokerCNY": brokercny.PrivateBrokerCNY(),
        }

        self.bid_fee_rate = 0.001
        self.ask_fee_rate = 0.001
        self.bid_price_risk = config.bid_price_risk
        self.ask_price_risk = config.ask_price_risk
        self.peer_exchange = self.hedger

        try:
            os.mkdir(self.out_dir)
        except:
            pass

        self.clients[self.exchange].cancel_all()

        logging.info('Setup complete')
        # time.sleep(2)

    def market_maker(self, depths):
        kexchange = self.exchange

        # update price
        try:
            bid_price = int(depths[self.exchange]["bids"][0]['price'])
            ask_price =  int(depths[self.exchange]["asks"][0]['price'])
            bid_amount = (depths[self.exchange]["bids"][0]['amount'])
            ask_amount=  (depths[self.exchange]["asks"][0]['amount'])

            bid1_price = int(depths[self.exchange]["bids"][1]['price'])
            ask1_price =  int(depths[self.exchange]["asks"][1]['price'])
            peer_bid_price = int(depths[self.peer_exchange]["bids"][0]['price'])
            peer_ask_price = int(depths[self.peer_exchange]["asks"][0]['price'])

        except  Exception as ex:
            logging.warn("exception depths:%s" % ex)
            traceback.print_exc()
            return

        if bid_price == 0 or ask_price == 0 or peer_bid_price == 0 or peer_bid_price == 0:
            logging.warn("exception ticker")
            return

        if bid_price+1 < ask_price :
            buyprice = bid_price + 1
        else:
            buyprice = bid_price

        if ask_price-1 > bid_price:
            sellprice = ask_price - 1
        else:
            sellprice = ask_price

        if buyprice == sellprice:
            if buyprice > bid_price:
                buyprice -=1
            elif sellprice < ask_price:
                sellprice +=1

        peer_bid_hedge_price = int(peer_bid_price*(1+self.bid_fee_rate))
        peer_ask_hedge_price = int(peer_ask_price*(1-self.ask_fee_rate))

        buyprice=min(buyprice, peer_bid_hedge_price) - self.bid_price_risk
        sellprice=max(sellprice, peer_ask_hedge_price) + self.ask_price_risk
        logging.info("sellprice/buyprice=(%s/%s)" % (sellprice, buyprice))

        self.buyprice = buyprice
        self.sellprice = sellprice

        # Update client balance
        self.update_balance()

        # query orders
        if self.is_buying():
            for buy_order in self.get_orders('buy'):
                logging.info(buy_order)
                result = self.clients[kexchange].get_order(buy_order['id'])
                logging.info (result)
                if not result:
                    logging.warn("get_order buy #%s failed" % (buy_order['id']))
                    return

                self.hedge_order(buy_order, result)

                if result['status'] == 'CLOSE' or result['status'] == 'CANCELED':
                    self.remove_order(buy_order['id'])
                else:
                    current_time = time.time()
                    if (result['price'] > buyprice or result['price'] < buyprice - config.MAKER_BUY_QUEUE*config.MAKER_BUY_STAGE):
                        logging.info("[TraderBot] cancel last buy trade " +
                                     "occured %.2f seconds ago" %
                                     (current_time - buy_order['time']))
                        logging.info("buyprice %s result['price'] = %s[%s],peer_bid_hedge_price=%s" % (buyprice, result['price'], result['price'] != buyprice,peer_bid_hedge_price))

                        self.cancel_order(kexchange, 'buy', buy_order['id'])


        if self.is_selling():
            for sell_order in self.get_orders('sell'):
                logging.info(sell_order)
                result = self.clients[kexchange].get_order(sell_order['id'])
                logging.info (result)
                if not result:
                    logging.warn("get_order sell #%s failed" % (sell_order['id']))
                    return

                self.hedge_order(sell_order, result)

                if result['status'] == 'CLOSE' or result['status'] == 'CANCELED':
                    self.remove_order(sell_order['id'])
                else:
                    current_time = time.time()
                    if (result['price'] < sellprice or result['price'] > sellprice + config.MAKER_SELL_QUEUE*config.MAKER_SELL_STAGE):
                        logging.info("[TraderBot] cancel last SELL trade " +
                                     "occured %.2f seconds ago" %
                                     (current_time - sell_order['time']))
                        logging.info("sellprice %s result['price'] = %s [%s],peer_ask_hedge_price=%s" % (sellprice, result['price'], result['price'] != sellprice, peer_ask_hedge_price))

                        self.cancel_order(kexchange, 'sell', sell_order['id'])

        # if ask_price*(1+2*self.bid_fee_rate) < peer_bid_price:
        #     logging.warn("eat to buy %s/%s", peer_bid_price, ask_price*(1+self.bid_fee_rate))
        #     self.new_order(kexchange, 'buy', maker_only=False, amount=ask_amount, price=ask_price)
        #     return

        # if bid_price*(1+2*self.ask_fee_rate) > peer_ask_price:
        #     logging.warn("eat to sell %s/%s", peer_ask_price, bid_price*(1+self.ask_fee_rate))
        #     self.new_order(kexchange, 'sell', maker_only=False, amount= bid_amount,  price=bid_price)
        #     return
            
        # excute trade
        if self.buying_len() < config.MAKER_BUY_QUEUE:
            self.new_order(kexchange, 'buy')
        if self.selling_len() < config.MAKER_SELL_QUEUE:
            self.new_order(kexchange, 'sell')


    def hedge_order(self, order, result):
        if result['deal_size'] <= 0:
            logging.debug("[hedger]NOTHING TO BE DEALED.")
            return

        logging.warn("[hedger]: %s", result)

        order_id = result['order_id']        
        deal_size = result['deal_size']
        price = result['avg_price']

        amount = deal_size - order['deal_amount']
        if amount <= config.broker_min_amount:
            logging.debug("[hedger]deal nothing while.")
            return

        client_id = str(order_id) + '-' + str(order['deal_index'])

        hedge_side = 'SELL' if result['side'] =='BUY' else 'BUY'
        logging.warn('[hedger] %s to broker: %s %s %s', client_id, hedge_side, amount, price)

        if hedge_side == 'SELL':
            self.clients[self.hedger].sell(amount, price, client_id)
        else:
            self.clients[self.hedger].buy(amount, price, client_id)

        # update the deal_amount of local order
        self.remove_order(client_id)
        order['deal_amount'] = deal_size
        order['deal_index'] +=1
        self.orders.append(order)
        
