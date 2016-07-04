# Copyright (C) 2013, Maxime Biais <maxime@biais.org>
# Copyright (C) 2016, Phil Song <songbohr@gmail.com>

import logging
import argparse
import sys
import public_markets
import glob
import os
import inspect
from arbitrer import Arbitrer
from logging.handlers import RotatingFileHandler
import lib.broker_api as exchange_api
from observers.emailer import send_email
import datetime

class ArbitrerCLI:
    def __init__(self):
        self.inject_verbose_info()

    def inject_verbose_info(self):
        logging.VERBOSE = 15
        logging.verbose = lambda x: logging.log(logging.VERBOSE, x)
        logging.addLevelName(logging.VERBOSE, "VERBOSE")

    def exec_command(self, args):
        logging.debug('exec_command:%s' % args)
        if "watch" in args.command:
            self.create_arbitrer(args)
            self.arbitrer.loop()
        if "replay-history" in args.command:
            self.create_arbitrer(args)
            self.arbitrer.replay_history(args.replay_history)
        if "get-balance" in args.command:
            self.get_balance(args)
        if "list-public-markets" in args.command:
            self.list_markets()
        if "get-broker-balance" in args.command:
            self.get_broker_balance(args)

    def list_markets(self):
        logging.debug('list_markets') 
        for filename in glob.glob(os.path.join(public_markets.__path__[0], "*.py")):
            module_name = os.path.basename(filename).replace('.py', '')
            if not module_name.startswith('_'):
                module = __import__("public_markets." + module_name)
                test = eval('module.' + module_name)
                for name, obj in inspect.getmembers(test):
                    if inspect.isclass(obj) and 'Market' in (j.__name__ for j in obj.mro()[1:]):
                        if not obj.__module__.split('.')[-1].startswith('_'):
                            print(obj.__name__)
        sys.exit(0)

    def get_balance(self, args):
        if not args.markets:
            logging.error("You must use --markets argument to specify markets")
            sys.exit(2)
        pmarkets = args.markets.split(",")
        pmarketsi = []
        for pmarket in pmarkets:
            exec('import private_markets.' + pmarket.lower())
            market = eval('private_markets.' + pmarket.lower()
                          + '.Private' + pmarket + '()')
            pmarketsi.append(market)
        for market in pmarketsi:
            print(market)

    def get_broker_balance(self, args):
        accounts = exchange_api.exchange_get_account()
        ticker = exchange_api.exchange_get_ticker()

        if accounts:
            cny_balance = 0
            btc_balance = 0
            cny_frozen = 0
            btc_frozen = 0
            broker_msg = '--------------------------broker balance report----------------------------\n\n'
            broker_msg += 'datetime\t\t %s\n' % str(datetime.datetime.now())
            for account in accounts:
                cny_balance += account.available_cny
                btc_balance += account.available_btc
                cny_frozen +=  account.frozen_cny
                btc_frozen +=  account.frozen_btc

                broker_msg +=  "%s:\t\t %s\n" % (account.exchange, str({"cny_balance": account.available_cny,
                                           "btc_balance": account.available_btc,
                                           "cny_frozen": account.frozen_cny,
                                           "btc_frozen": account.frozen_btc}))
                # broker_msg += '---------------------------\n'

            broker_msg +=  "%s:\t\t %s\n" % ('All   ', str({"cny_balance": cny_balance,
                                           "btc_balance": btc_balance,
                                           "cny_frozen": cny_frozen,
                                           "btc_frozen": btc_frozen}))
            broker_msg +=  "%s:\t\t %s\n" % ('Price', str({"ask": '%.2f' % ticker.ask,
                                           "bid": '%.2f' % ticker.bid}))
            
            broker_msg +=  "%s:\t %s\n" % ('Converted', str({"cny": '%.2f' % ((btc_balance+btc_frozen)*ticker.bid + cny_balance+cny_frozen),
                                                        "btc": '%.2f' % (btc_balance+btc_frozen + (cny_balance+cny_frozen)/ticker.ask)}))

            broker_msg += '\n------------------------------------------------------------------------------------\n'

            send_email('broker balance report', broker_msg)

    def create_arbitrer(self, args):
        self.arbitrer = Arbitrer()
        if args.observers:
            self.arbitrer.init_observers(args.observers.split(","))
        if args.markets:
            self.arbitrer.init_markets(args.markets.split(","))

    def init_logger(self, args):
        level = logging.INFO
        if args.verbose:
            level = logging.VERBOSE
        if args.debug:
            level = logging.DEBUG
        logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',
                            level=level)

        Rthandler = RotatingFileHandler('arbitrage.log', maxBytes=100*1024*1024,backupCount=10)
        Rthandler.setLevel(level)
        formatter = logging.Formatter('%(asctime)-12s [%(levelname)s] %(message)s')  
        Rthandler.setFormatter(formatter)
        logging.getLogger('').addHandler(Rthandler)

        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)

    def main(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-d", "--debug", help="debug verbose mode",
                            action="store_true")
        parser.add_argument("-v", "--verbose", help="info verbose mode",
                            action="store_true")
        parser.add_argument("-o", "--observers", type=str,
                            help="observers, example: -oLogger,Emailer")
        parser.add_argument("-m", "--markets", type=str,
                            help="markets, example: -mHaobtcCNY,Bitstamp")
        parser.add_argument("command", nargs='*', default="watch",
                            help='verb: "watch|replay-history|get-balance|list-public-markets"')
        args = parser.parse_args()
        self.init_logger(args)
        self.exec_command(args)

def main():
    cli = ArbitrerCLI()
    cli.main()

if __name__ == "__main__":
    main()
