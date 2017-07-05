# Copyright (C) 2017, Kirill Bespalov <k.besplv@gmail.com>

import json
import logging
import time

import tenacity
import pika

from pika.exceptions import AMQPError
from tenacity import stop_after_delay, wait_exponential
from arbitrage.observers.observer import ObserverBase

LOG = logging.getLogger(__name__)


class AMQPClient(object):
    """Represents the AMQP client to send an opportunity given by watcher"""

    def __init__(self, config):
        self.config = config
        self.message_ttl = str(self.config.market_expiration_time * 1000)
        self.report_queue = self.config.report_queue
        self.params = pika.URLParameters(self.config.amqp_url)
        self._connection = None
        self._channel = None

    def ensure_connected(self):
        """Ensure that connection is established"""
        try:
            if not self._connection or not self._connection.is_open:
                self._connection = pika.BlockingConnection(self.params)
            if not self._channel or not self._connection.is_open:
                self._channel = self._connection.channel()
                self._channel.queue_declare(self.config.report_queue)
        except AMQPError:
            LOG.error('Failed to establish connection. Retrying')
            raise
        LOG.debug('AMQP connection to %s was successfully established' %
                  self.config.amqp_url)
        return True

    @property
    def channel(self):
        if not self._connection or not self._channel.is_open:
            stop = stop_after_delay(self.config.market_expiration_time)
            wait = wait_exponential(max=5)
            retry = tenacity.retry(stop=stop, wait=wait)
            retry(self.ensure_connected)()

        return self._channel

    def push(self, data):
        """Push a data to the exchange"""
        try:
            properties = pika.BasicProperties(
                content_type='application/json',
                expiration=self.message_ttl,
                timestamp=int(time.time())
            )
            self.channel.basic_publish(exchange='',
                                       routing_key=self.report_queue,
                                       body=json.dumps(data),
                                       properties=properties)
        except Exception:
            LOG.error('Failed to push a message')


class Rabbitmq(ObserverBase):
    """Represent AMQP based arbitrage opportunity observer"""

    def __init__(self, config):
        super().__init__(config)
        self.client = AMQPClient(config)

    def opportunity(self, profit, volume, buyprice, kask, sellprice, kbid,
                    perc, weighted_buyprice, weighted_sellprice):
        """Sends opportunity to a message queue"""

        # split market name and currency:  KrakenUSD -> (Kraken, USD)
        buy_exchange, buy_currency = kask[:-3], kask[-3:]
        sell_exchange, sell_currency = kbid[:-3], kbid[-3:]

        message = {"order_type": "inter_exchange_arb",
                   "order_specs": {
                       "arb_volume": volume,
                       "arb_currency": "BTC",
                       "buy_currency": buy_currency,
                       "sell_currency": sell_currency,
                       "buy_exchange": buy_exchange,
                       "sell_exchange": sell_exchange
                   }}

        self.client.push(message)
