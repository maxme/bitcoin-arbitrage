import time
import unittest
from arbitrage.manager import ArbiterService


class TestArbitrageService(unittest.TestCase):
    def setUp(self):
        self.service = ArbiterService()
        self.markets = [
            "BtceUSD",
            "CoinBaseUSD",
            "GeminiUSD",
            "KrakenUSD",
        ]

    def test_stop_start(self):
        self.assertTrue(self.service.stop())
        time.sleep(1)
        self.assertFalse(self.service.status()['is_started'])
        self.test_start()

    def test_start(self):
        self.service.start({'markets': self.markets})
        time.sleep(5)
        self.assertTrue(self.service.status()['is_started'])
