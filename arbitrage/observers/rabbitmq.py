# Copyright (C) 2017, Kirill Bespalov <k.besplv@gmail.com>

import json
import logging
import importlib

import tenacity
import pika
from pika.exceptions import AMQPError
from tenacity import stop_after_delay, wait_exponential
from arbitrage.observers.observer import Observer

LOG = logging.getLogger(__name__)

config = None
try:
    config = importlib.import_module('arbitrage.config')
except ImportError:
    LOG.warn('Failed to import config.py')


class AMQPClient(object):
    """Represents the AMQP client to send an opportunity given by watcher"""

    def __init__(self, configuration=None):
        self.config = configuration or config
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
                expiration=self.message_ttl
            )
            self.channel.basic_publish(exchange='',
                                       routing_key=self.report_queue,
                                       body=json.dumps(data),
                                       properties=properties)
        except Exception:
            LOG.exception('Failed to push a message')


class Rabbitmq(Observer):
    """Represent the observer based on message queue"""

    def __init__(self, configuration=None):
        self.config = configuration or config
        self.client = AMQPClient(self.config)

    def opportunity(self, profit, volume, buyprice, kask, sellprice, kbid,
                    perc, weighted_buyprice, weighted_sellprice):
        message = {
            'profit': profit,
            'volume': volume,
            'buy_price': buyprice,
            'kask': kask,
            'sell_price': sellprice,
            'kbid': kbid,
            'perc': perc,
            'weighted_buy_price': weighted_buyprice,
            'weighted_sell_price': weighted_sellprice
        }

        self.client.push(message)
