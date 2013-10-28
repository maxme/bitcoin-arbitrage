# Copyright (C) 2013, Maxime Biais <maxime@biais.org>
# Copyleft (c) 2013, Ryan Casey <ryepdx@gmail.com>

import logging
import argparse
import sys

from arbitrer import Arbitrer


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
        parser = argparse.ArgumentParser()
        parser.add_argument("-v", "--verbose", help="more verbose",
                            action="store_true")
        parser.add_argument("-o", "--observers", type=str,
                            help="observers, example: -oLogger,Emailer")
        parser.add_argument("-m", "--markets", type=str,
                            help="markets, example: -mMtGox,Bitstamp")
        parser.add_argument("command", nargs='*', default="watch",
                            help='verb: "watch|replay-history|get-balance"')
        args = parser.parse_args()

        level = logging.INFO
        if args.verbose:
            level = logging.DEBUG
        logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',
                            level=level)

        self.create_arbitrer(args)
        self.exec_command(args)


def main():
    cli = ArbitrerCLI()
    cli.main()


if __name__ == "__main__":
    main()
