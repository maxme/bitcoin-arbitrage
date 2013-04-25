# Copyright (C) 2013, Maxime Biais <maxime@biais.org>

import sys
import unittest
sys.path.append('../')
import arbitrage
from private_markets.bitcoincentral import PrivateBitcoinCentral


class TestArbitrage(unittest.TestCase):
    def setUp(self):
        pass

    def test_getinfos(self):
        pv_btcentral = PrivateBitcoinCentral()

if __name__ == '__main__':
    unittest.main()
