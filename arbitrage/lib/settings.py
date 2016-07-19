import os
import sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

HAOBTC_API_URL = {
                  'host' :'api.haobtc.com',
                  'trade':'https://api.haobtc.com/exchange/api/v1/trade',
                  'cancel_order':'https://api.haobtc.com/exchange/api/v1/cancel_order',
                  'order_info':'https://api.haobtc.com/exchange/api/v1/order_info',
                  'orders_info':'https://api.haobtc.com/exchange/api/v1/orders_info',
                  'history_info':'https://api.haobtc.com/exchange/api/v1/history_info',
                  'account_info':'https://api.haobtc.com/exchange/api/v1/account_info',
                  'ticker':'https://api.haobtc.com/exchange/api/v1/ticker' ,
                  'depth':'https://api.haobtc.com/exchange/api/v1/depth',
                  'batch_trade':'https://api.haobtc.com/exchange/api/v1/batch_trade',
                  'cancel_all':'https://api.haobtc.com/exchange/api/v1/cancel_all',
                  'cancel_list':'https://api.haobtc.com/exchange/api/v1/cancel_list',
                  'fast_ticker':'https://api.haobtc.com/api/v1/price/cny',
                  }
HAOBTC_API = {'fee':0.001}

HUOBI_API_URL = {
                  'host':'api.huobi.com/apiv3',
                  'ticker':'http://api.huobi.com/staticmarket/ticker_btc_json.js',
                  'depth':'http://api.huobi.com/staticmarket/depth_btc_json.js',
                  'data':'http://api.huobi.com/staticmarket/detail_btc_json.js',
                  'buy' : 'buy',
                  'buy_market':  'buy_market',
                  'cancel_order': 'cancel_order',
                  'account_info': 'get_account_info',
                  'new_deal_orders': 'get_new_deal_orders',
                  'order_id_by_trade_id': 'get_order_id_by_trade_id',
                  'get_orders': 'get_orders',
                  'order_info': 'order_info',
                  'sell': 'sell',
                  'sell_market': 'sell_market',
                }


OKCOIN_API_URL = {
                   'host':'www.okcoin.cn',
                   'ticker': 'https://www.okcoin.cn/api/v1/ticker.do',
                   'depth': 'https://www.okcoin.cn/api/v1/depth.do',
                   'tradesInfo':'https://www.okcoin.cn/api/v1/trades.do',
                   'userInfo':'https://www.okcoin.cn/api/v1/userinfo.do',
                   'trade':'https://www.okcoin.cn/api/v1/trade.do',
                   'batch_trade':'https://www.okcoin.cn/api/v1/batch_trade.do',
                   'cancel_order':'https://www.okcoin.cn/api/v1/cancel_order.do',
                   'order_info':'https://www.okcoin.cn/api/v1/order_info.do',
                   'order_history':'https://www.okcoin.cn/api/v1/order_history.do'
                }

OKCOIN_MIN_TRADE = {'buy':0.01,'sell':0.01 , 'trade':0.01}
OKCOIN_API = {'max_open_order':50,'fee':0.004}


#IMPORT local_settings
try:
    from .local_settings import *
except ImportError:
    pass

