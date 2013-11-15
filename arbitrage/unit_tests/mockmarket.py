from arbitrage.public_markets.market import Market


class MockMarket(Market):
    def __init__(self, **kwargs):
        super(MockMarket, self).__init__(**kwargs)
        self.update_rate = 0
        self.trade_fee = 0
        self.depth = {'asks': [{'price': 0, 'amount': 0}], 'bids': [{'price': 0, 'amount': 0}]}
        self.mock_depth = {'asks': [{'price': 0, 'amount': 0}], 'bids': [{'price': 0, 'amount': 0}]}

    def update_depth(self):
        self.depth = self.mock_depth

    def set_mock_depth(self, depth):
        self.mock_depth = depth

