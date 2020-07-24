# Copyright (C) 2013, Maxime Biais <maxime@biais.org>

import logging
import argparse
import sys
import glob
import os
import inspect
from arbitrage.arbitrer import Arbitrer
from arbitrage import public_markets


class ArbitrerCLI:
    def __init__(self):
        self.inject_verbose_info()

    def inject_verbose_info(self):
        logging.VERBOSE = 15
        logging.verbose = lambda x: logging.log(logging.VERBOSE, x)
        logging.addLevelName(logging.VERBOSE, "VERBOSE")

    def exec_command(self, args):
        if "watch" in args.command:
            self.create_arbitrer(args).loop()
        if "replay-history" in args.command:
            self.create_arbitrer(args)
            self.arbitrer.replay_history(args.replay_history)
        if "get-balance" in args.command:
            self.get_balance(args)
        if "list-public-markets" in args.command:
            self.list_markets()
        if "compare-depths" in args.command:
            self.compare_depths(args)
      
        if "generate-config" in args.command:
            self.generate_sample_config()


    def compare_depths(self, args):
        if not args.exchanges:
            logging.error("You must use --exchanges argument to specify exchanges")
            sys.exit(2)
        pexchanges = args.exchanges.split(",")
        pexchangei = []
        for pexchange in pexchanges:
            exec("import arbitrage.public_markets._" + pexchange.lower())

            # FIXME: Fix the following hard-coded USDT and btc_usdt
            market = eval( 
                "arbitrage.public_markets._" + pexchange.lower() + "." + pexchange + "('USDT','btc_usdt').update_depth().depth_1pct()"
            )
            pexchangei.append( ('1%', pexchange,market) )
            market = eval(
                "arbitrage.public_markets._" + pexchange.lower() + "." + pexchange + "('USDT','btc_usdt').update_depth().depth_01pct()"
            )
            pexchangei.append( ('0.1%', pexchange,market) )

        for market in pexchangei:
            print(market)
        
        sys.exit(0)

    def get_market_list(self):
        markets = []
        for filename in glob.glob(os.path.join(public_markets.__path__[0], "*.py")):
            module_name = os.path.basename(filename).replace(".py", "")
            if not module_name.startswith("_"):
                module = __import__("arbitrage.public_markets." + module_name)
                test = eval("module.public_markets." + module_name)
                for name, obj in inspect.getmembers(test):
                    if inspect.isclass(obj) and "Market" in (j.__name__ for j in obj.mro()[1:]):
                        if not obj.__module__.split(".")[-1].startswith("_"):
                            markets.append(obj.__name__)
        return markets

    def list_markets(self):
        markets = self.get_market_list()
        markets.sort()
        print("\n".join(markets))
        sys.exit(0)

    def generate_sample_config(self):
        markets = self.get_market_list()
        markets.sort()
        print("markets = [")
        print('",\n'.join(['  "' + i for i in markets]) + '"')
        print("]")
        print('observers = ["Logger"]')
        print("""
refresh_rate = 60
market_expiration_time = 120  # in seconds: 2 minutes

# SafeGuards
max_tx_volume = 1  # in BTC
min_tx_volume = 0.01  # in BTC
balance_margin = 0.05  # 5%
profit_thresh = 0  # in USD
perc_thresh = 0  # in %""")
        sys.exit(0)

    def get_balance(self, args):
        if not args.markets:
            logging.error("You must use --markets argument to specify markets")
            sys.exit(2)
        pmarkets = args.markets.split(",")
        pmarketsi = []
        for pmarket in pmarkets:
            exec("import arbitrage.private_markets." + pmarket.lower())
            market = eval(
                "arbitrage.private_markets." + pmarket.lower() + ".Private" + pmarket + "()"
            )
            pmarketsi.append(market)
        for market in pmarketsi:
            print(market)

    def create_arbitrer(self, args):
        self.arbitrer = Arbitrer()
        if args.observers:
            self.arbitrer.init_observers(args.observers.split(","))
        if args.markets:
            self.arbitrer.init_markets(args.markets.split(","))
        return self.arbitrer

    def init_logger(self, args):
        level = logging.INFO
        if args.verbose:
            level = logging.VERBOSE
        if args.debug:
            level = logging.DEBUG
        logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=level)

    def main(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-d", "--debug", help="debug verbose mode", action="store_true")
        parser.add_argument("-v", "--verbose", help="info verbose mode", action="store_true")
        parser.add_argument(
            "-o", "--observers", type=str, help="observers, example: -oLogger,Emailer"
        )
        parser.add_argument(
            "-m", "--markets", type=str, help="markets, example: -m BitstampEUR,KrakenEUR"
        )
        parser.add_argument(
            "-e", "--exchanges", type=str, help="exchanges, example: -e OKCoin"
        )
        parser.add_argument(
            "command",
            nargs="*",
            default="watch",
            help='verb: "watch|replay-history|get-balance|list-public-markets|compare-depths"',
        )
        args = parser.parse_args()
        self.init_logger(args)
        self.exec_command(args)


def main():
    cli = ArbitrerCLI()
    cli.main()


if __name__ == "__main__":
    main()
