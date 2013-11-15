# Copyright (C) 2013, Maxime Biais <maxime@biais.org>
# Copyleft (c) 2013, Ryan Casey <ryepdx@gmail.com>

import logging
import argparse
import sys
import config_dynamic
from arbitrer import Arbitrer

if hasattr(sys, 'frozen'):
    # Logging needs to be set up here if running as a compiled executable.
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',
        level=logging.INFO)



class ArbitrerCLI:
    def __init__(self):
        pass

    def exec_command(self, args):

        if "watch" in args.command:
            logging.info("Looking for profits along %s possible paths." % (
                len(self.arbitrer.marketchains)
            ))
            self.arbitrer.loop()

        if "replay-history" in args.command:
            self.arbitrer.replay_history(args.replay_history)

        if "get-balance" in args.command:
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


    def create_arbitrer(self, args):
        self.arbitrer = Arbitrer()
        if args.observers:
            self.arbitrer.init_observers(args.observers.split(","))
        if args.markets:
            self.arbitrer.init_markets(args.markets.split(","))


    def main(self):
        compiled = hasattr(sys, 'frozen')
        parser = argparse.ArgumentParser()
        parser.add_argument("-o", "--observers", type=str,
                            help="observers, example: -oLogger,Emailer")
        parser.add_argument("-m", "--markets", type=str,
                            help="markets, example: -mMtGox,Bitstamp")
        parser.add_argument("command", nargs='*', default="watch",
                            help='verb: "watch|replay-history|get-balance"')

        # cx_freeze seems to have problems with setting logging down here.
        if not compiled:
            parser.add_argument("-v", "--verbose", help="more verbose",
                                action="store_true")

        args = parser.parse_args()
        
        if not compiled:
            logging.basicConfig(
                format='%(asctime)s [%(levelname)s] %(message)s',
                level=(logging.DEBUG if args.verbose else logging.INFO)
            )

        logging.info("Starting arbitrage. Ctrl-C at any time to exit.")
        config_dynamic.init()

        self.create_arbitrer(args)
        self.exec_command(args)


def main():
    cli = ArbitrerCLI()
    cli.main()


def log_config_json_loaded(config):
    logging.info("Loaded settings from config.json")

def log_config_json_error(e):
    logging.warn("Could not load config.json")

if __name__ == "__main__":
    try:
        config_dynamic.loaded.connect(log_config_json_loaded)
        config_dynamic.error.connect(log_config_json_error)
        main()
    except KeyboardInterrupt:
        logging.info("Stopping arbitrage and exiting.")
