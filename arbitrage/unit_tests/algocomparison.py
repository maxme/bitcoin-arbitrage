import sys

sys.path.append('../')
import unittest

from arbitrage.arbitrer import Arbitrer
from arbitrage.arbitrerNG import ArbitrerNG
from arbitrage.public_markets.bitstampusd import BitstampUSD
from arbitrage.public_markets.campbxusd import CampBXUSD
from arbitrage.public_markets.mtgoxusd import MtGoxUSD

import json


class TestCompareArbitrage(unittest.TestCase):
    def setUp(self):
        self.arbitrer = Arbitrer()
        self.arbitrerNG = ArbitrerNG()

        bs = BitstampUSD()
        bs_file = open('bitstamp_data.json', 'r')
        bs_depth = json.loads(bs_file.read())
        bs_file.close()
        self.bs_data = bs.format_depth(bs_depth)

        cbx = CampBXUSD()
        cbx_file = open('cbx_data.json', 'r')
        cbx_depth = json.loads(cbx_file.read())
        cbx_file.close()
        self.cbx_data = cbx.format_depth(cbx_depth)

        mt = MtGoxUSD()
        mt_file = open('mtgox_data.json', 'r')
        mt_depth = json.loads(mt_file.read())["data"]
        mt_file.close()
        self.mt_data = mt.format_depth(mt_depth)


    def test_compare_arbitrage_depth_opportunity_1(self):
        self.arbitrer.depths = {'AAA': self.bs_data, 'BBB': self.cbx_data}
        self.arbitrerNG.depths = {'AAA': self.bs_data, 'BBB': self.cbx_data}
        self._do_compare()

    def test_compare_arbitrage_depth_opportunity_2(self):
        self.arbitrer.depths = {'AAA': self.bs_data, 'BBB': self.mt_data}
        self.arbitrerNG.depths = {'AAA': self.bs_data, 'BBB': self.mt_data}
        self._do_compare()

    def test_compare_arbitrage_depth_opportunity_3(self):
        self.arbitrer.depths = {'AAA': self.cbx_data, 'BBB': self.mt_data}
        self.arbitrerNG.depths = {'AAA': self.cbx_data, 'BBB': self.mt_data}
        self._do_compare()


    def _do_compare(self):
        print("profit, volume, buyprice, sellprice, weighted_buyprice, weighted_sellprice")

        T1 = self.arbitrer.arbitrage_depth_opportunity('AAA', 'BBB')
        val1 = [v for v in T1]
        print(','.join(str(v) for v in T1))
        T2 = self.arbitrerNG.arbitrage_depth_opportunity('AAA', 'BBB', 10)
        val2 = [v for v in T2]
        print(','.join(str(v) for v in T2))

        # les tuples marchent pas bien avec les assert quand ils sont KO... à creuser
        # pb lié au plugin 'nose manager'
        # assert T1 == T2
        for (a, b) in zip(val1, val2):
            assert a == b

        T = self.arbitrer.arbitrage_depth_opportunity('BBB', 'AAA')
        print(','.join(str(v) for v in T))
        T = self.arbitrerNG.arbitrage_depth_opportunity('BBB', 'AAA', 10)
        print(','.join(str(v) for v in T))


if __name__ == '__main__':
    unittest.main()
