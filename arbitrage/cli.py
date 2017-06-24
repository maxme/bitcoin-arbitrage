# Copyright (C) 2013, Maxime Biais <maxime@biais.org>

import logging
import argparse
import sys
import glob
import os
import inspect

from arbitrage import public_markets
from arbitrage.arbiter import Arbiter
from arbitrage import config


class ArbiterCLI:

    def exec_command(self, args):
        if "watch" in args.command:
            self.create_arbiter(args)
            self.arbiter.loop()
        if "replay-history" in args.command:
            self.create_arbiter(args)
            self.arbiter.replay_history(args.replay_history)
        if "get-balance" in args.command:
            self.get_balance(args)
        if "list-public-markets" in args.command:
            self.list_markets()

    def list_markets(self):
        for filename in glob.glob(
                os.path.join(public_markets.__path__[0], "*.py")):
            module_name = os.path.basename(filename).replace('.py', '')
            if not module_name.startswith('_'):
                module = __import__("public_markets." + module_name)
                test = eval('module.' + module_name)
                for name, obj in inspect.getmembers(test):
                    if inspect.isclass(obj) and 'Market' in (j.__name__ for j
                                                             in obj.mro()[1:]):
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

    def create_arbiter(self, args):
        if args.observers:
            given = args.observers.split(",")
            config.observers = list(set(config.observers) | set(given))
        if args.markets:
            given = args.markets.split(",")
            config.markets = list(set(config.markets) | set(given))
        self.arbiter = Arbiter()

    def init_logger(self, args):
        level = logging.INFO
        if args.debug:
            level = logging.DEBUG
        logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',
                            level=level)

    def main(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-d", "--debug", help="debug verbose mode",
                            action="store_true")
        parser.add_argument("-o", "--observers", type=str,
                            help="observers, example: -oLogger,Emailer")
        parser.add_argument("-m", "--markets", type=str,
                            help="markets, example: -mMtGox,Bitstamp")
        parser.add_argument("command", nargs='*', default="watch",
                            help='verb: "watch|replay-history|get-balance|'
                                 'list-public-markets"')
        args = parser.parse_args()
        self.init_logger(args)
        self.exec_command(args)


def main():
    cli = ArbiterCLI()
    cli.main()


if __name__ == "__main__":
    main()
