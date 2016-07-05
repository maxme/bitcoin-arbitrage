import thriftpy
broker_thrift = thriftpy.load("arbitrage/lib/broker.thrift", module_name="broker_thrift")

from thriftpy.rpc import make_client
from thriftpy.protocol.binary import TBinaryProtocolFactory
from thriftpy.transport.framed import TFramedTransportFactory

import config
import logging

client = make_client(broker_thrift.TradeService, config.BROKER_HOST, config.BROKER_PORT,
                           proto_factory=TBinaryProtocolFactory(),
                           trans_factory=TFramedTransportFactory())

def exchange_ping():
  client.ping()
  return

def exchange_get_status():  
  logging.debug('exchange_get_status')
  exchange_status = client.get_exchange_status()
  logging.debug('exchange_get_status %s', exchange_status)

  return exchange_status

def exchange_check_price(price, trade_type):
  logging.debug('check_price %s %s', price, trade_type)
  client.check_price(price, trade_type)
  logging.debug("exchange_check_price-> end")
  
  return

def exchange_buy(client_id, btc, price):
  logging.debug('exchange_buy %s %s %s', client_id, btc, price)
  buyOrder = broker_thrift.Trade(str(client_id), btc, price)
  client.buy(buyOrder)
  logging.debug("exchange_buy-> end")
  
  return

def exchange_sell(client_id, btc, price):
  logging.debug('exchange_sell %s %s %s', client_id, btc, price)
  sellOrder = broker_thrift.Trade(str(client_id), btc, price)
  client.sell(sellOrder)
  logging.debug("exchange_sell-> end")
    
  return
    
def exchange_get_ticker():
  logging.debug('get_ticker')
  ticker= client.get_ticker()
  logging.debug("get_ticker-> %s",ticker)

  return ticker
    
def exchange_get_account():
  logging.debug("get_account")
  accounts= client.get_account()
  logging.debug("get_account-> %s",accounts)

  return accounts
    
def exchange_get_alert_orders():
  logging.debug("get_alert_orders")
  alert_orders= client.get_alert_orders()
  logging.debug("get_alert_orders-> %s",alert_orders)

  return alert_orders

   
def exchange_config_keys(exchange_configs):
  logging.debug("config_keys->begin")
  client.config_keys(exchange_configs)
  logging.debug("config_keys->end")

  return

def exchange_config_amount(amount_config):
  logging.debug("config_amount->%s", amount_config)
  client.config_amount(amount_config)
  logging.debug("config_amount->end")

  return

