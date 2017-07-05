from arbitrage.markets._gemini import GeminiBase


class GeminiUSD(GeminiBase):
    def __init__(self, config=None):
        super().__init__("USD", "btcusd", config)
