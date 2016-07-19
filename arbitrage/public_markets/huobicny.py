# Copyright (C) 2016, Philsong <songbohr@gmail.com>

from ._huobi import Huobi

class HuobiCNY(Huobi):
    def __init__(self):
        super().__init__("CNY", "btc")
