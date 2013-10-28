import logging
import config
import time
from decimal import Decimal
from .observer import Observer
from .emailer import send_email
from private_markets import mtgox
from private_markets import bitstamp


class TraderBot(Observer):
    def __init__(self, clients = None):
        self.trade_wait = 120  # in seconds
        self.last_trade = 0
        self.potential_trades = []

        if clients:
            self.clients = clients
        else:
            self.clients = {
                "MtGox": mtgox.PrivateMtGox(),
                "Bitstamp": bitstamp.PrivateBitstamp(),
            }

    def begin_opportunity_finder(self, depths):
        self.potential_trades = []

    def end_opportunity_finder(self):
        if not self.potential_trades:
            return
        self.potential_trades = sorted(
            self.potential_trades, key=lambda trade: trade.profit
        )
        # Execute only the best (more profitable)
        self.execute(self.potential_trades[-1])

    def update_balance(self):
        for kclient in self.clients:
            self.clients[kclient].get_info()

    def opportunity(self, tradechains):
        tradechain = sorted(tradechains, key=lambda trade: trade.profit)[-1]
        if tradechain.profit < config.profit_thresh \
        or tradechain.percentage < config.perc_thresh:
            logging.debug("[TraderBot] Profit or profit percentage lower than"+
                          " thresholds")
            return

        self.update_balance()
        
        scaling_factors = [1]

        for trade in tradechain.trades:
            market_name = trade.market_name
            if market_name not in self.clients:
                logging.warn("[TraderBot] Can't automate this trade, client "+
                            "not available: %s" % market_name)
                return

            balance = self.clients[market_name].balance(trade.from_currency)

            if balance <= 0:
                logging.warn("[TraderBot] Can't automate this trade. Out of "+
                    "%s on %s" % (trade.from_currency, market_name)
                )
                return

            scaling_factors.append(
                Decimal(str(balance)) / Decimal(str(trade.from_volume))
            )

        tradechain.scale(min(scaling_factors))
        volume = min(config.max_tx_volume, tradechain.trades[0].from_volume)

        if volume < config.min_tx_volume:
            logging.warn("Can't automate this trade, minimum volume "+
                        " transaction not reached %f/%f" % (
                        volume, config.min_tx_volume)
            )
            for trade in tradechain.trades:
                logging.warn("Balance on %s: %f %s" % (trade.market_name,
                    self.clients[trade.market_name].balance(
                        trade.from_currency
                    ), trade.from_currency)
                )
            return

        current_time = time.time()
        if current_time - self.last_trade < self.trade_wait:
            logging.warn("[TraderBot] Can't automate this trade, last trade " +
                         "occured %.2f seconds ago" %
                         (current_time - self.last_trade))
            return
        self.potential_trades.append(tradechain)

    def watch_balances(self):
        pass

    def execute(self, tradechain):
        self.last_trade = time.time()

        for trade in tradechain.trades:
            logging.info("[TradeBot] Executing \"%s\"" % str(trade))
            self.clients[trade.market_name].execute(trade)
