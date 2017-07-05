import os

from arbitrage import registry


class ConfigBase(object):
    def __init__(self):
        self.opts = []


class RabbitmqCfgMixin(ConfigBase):
    """Represent required for the :Rabbitmq observer configs"""

    def __init__(self):
        super().__init__()

        default = 'amqp://guest:guest@localhost:5672/'
        self.amqp_url = os.getenv('CLOUDAMQP_URL', default)
        self.report_queue = 'arbitrage_watcher'
        self.opts.extend(['report_queue', 'amqp_url'])


class Configuration(RabbitmqCfgMixin):
    """Represent the minimal config opts required for the :Arbiter"""

    def __init__(self):
        self.opts = []

        super().__init__()
        self.refresh_rate = 20
        self.default_market_update_rate = 20
        self.bank_fee = 0.007
        self.fiat_update_delay = 3600
        self.market_expiration_time = 120
        self.max_tx_volume = 10
        self.observers = ['Logger']
        self.markets = list(registry.markets_registry.keys())
        self.opts.extend([
            'default_market_update_rate',
            'market_expiration_time',
            'fiat_update_delay',
            'max_tx_volume',
            'refresh_rate',
            'observers',
            'bank_fee',
            'markets'
        ])

    def as_dict(self):
        """Returns dict representation of the configuration opts"""
        return {k: getattr(self, k, None) for k in self.opts}

    def update(self, config: dict):
        """Update configuration values from :config"""
        for key in config:
            setattr(self, key, config.get(key))
        return self
