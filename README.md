# bitcoin-arbitrage

Bitcoin arbitrage - opportunity detector

# config

First

    cp src/config.py-example src/config.py

Then edit config.py file to setup your preferences (watched markets) and callback (like sending an email, a jabber msg, run trading bot)

It fetch data from bitcoincharts API (most of markets) and bitcoin-central API.

# run

    $ python src/arbitrage.py
    ticker mtgoxEUR: 15.2700/15.2900 - intrsngEUR: 14.5000/14.5500 - bc2EUR: 15.5500/16.0000 -
    31/01/2013 13:18:29 - buy at 15.2900 (mtgoxEUR) and sell at 15.5500 (bc2EUR) - 1.6720%
    31/01/2013 13:18:29 - buy at 14.5500 (intrsngEUR) and sell at 15.2000 (mtgoxEUR) - 4.2763%
    31/01/2013 13:18:29 - buy at 14.5500 (intrsngEUR) and sell at 15.5500 (bc2EUR) - 6.4309%


# LICENSE

MIT
