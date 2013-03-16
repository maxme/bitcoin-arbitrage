# bitcoin-arbitrage - opportunity detector and automated trading

Bitcoin arbitrage - opportunity detector.

It gets order books from supported exchanges API, currently:
 - Bitcoin24
 - Bitcoin-Central
 - Intersango
 - Bitstamp
 - MtGox

To add a new exchange see this [doc/add-new-exchange.md](doc/add-new-exchange.md)

# WARNING

**Real trading bots are included in this version. Don't use them if you don't know what you are doing.**

# Configuration

    cp src/config.py-example src/config.py

Then edit config.py file to setup your preferences: watched markets and observers


# Run

    $ python src/arbitrage.py
    2013-03-12 03:52:14,341 [INFO] profit: 30.539722 EUR with volume: 10 BTC - buy at 29.3410 (MtGoxEUR) sell at 29.4670 (Bitcoin24EUR) ~10.41%
    2013-03-12 03:52:14,356 [INFO] profit: 66.283642 EUR with volume: 10 BTC - buy at 29.3410 (MtGoxEUR) sell at 30.0000 (BitcoinCentralEUR) ~22.59%
    2013-03-12 03:52:14,357 [INFO] profit: 31.811390 EUR with volume: 10 BTC - buy at 29.3410 (MtGoxEUR) sell at 30.0000 (IntersangoEUR) ~10.84%
    2013-03-12 03:52:45,090 [INFO] profit: 9.774324 EUR with volume: 10 BTC - buy at 35.3630 (Bitcoin24EUR) sell at 35.4300 (BitcoinCentralEUR) ~2.76%

# TODO

 * Tests
 * Update order books with a WebSocket client for supported exchanges (MtGox, Bitcoin-Central)
 * Better documentation
 * Add fiat currency converters USD / EUR
 * Replace float by Decimal
 * Better history handling for observer "HistoryDumper" (Redis ?)
 * Move EUR / USD from a market to an other:
   * Coupons
   *
   * Negative Operations

# LICENSE

MIT

Copyright (c) 2013 Maxime Biais <firstname.lastname@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
