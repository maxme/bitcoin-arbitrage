## How to install

```
cd ./bitcoin-arbitrage/
pip install .
```


## Supported markets:

```
- CampBXUSD
- CoinBaseUSD
- OKCoinCNY
- BtceUSD
- BTCCCNY
- BtceEUR
- BitstampUSD
- GeminiUSD
- BitfinexUSD
- KrakenUSD
- PaymiumEUR
- KrakenEUR
```

## Supported observers

```
Logger
Rabbitmq
```

## How to use:

Default configuration


```python

import logging
import time

from arbitrage.arbiter import Arbiter
from arbitrage.config import Configuration

log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=log_format, level=logging.INFO)

config = Configuration()
arbiter = Arbiter(config)

while 1:
    arbiter.depths = arbiter.update_depths()
    arbiter.tickers()
    arbiter.tick()
    time.sleep(config.refresh_rate)
    
```

RabbitMQ observer:

```python


import logging
import time

from arbitrage.arbiter import Arbiter
from arbitrage.config import Configuration

log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=log_format, level=logging.INFO)

config = Configuration()
config.amqp_url = 'http://guest:guest@localhost'
config.observers = ['Logger','Rabbitmq']
arbiter = Arbiter(config)

while 1:
    arbiter.depths = arbiter.update_depths()
    arbiter.tickers()
    arbiter.tick()
    time.sleep(config.refresh_rate)

```

## Configuration options

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**bank_fee** | **float** | Bank fees accounting at conversion | [optional] [default to 0.007]
**default_market_update_rate** | **int** | Default market&#39;s depth update rate in seconds | [optional] [default to 20]
**fiat_update_delay** | **int** | Delay in seconds between an exchange rate updates | [optional] 
**market_expiration_time** | **int** | Markets order book expiration time | [optional] 
**markets** | **list[str]** | List of market names | [optional] 
**max_tx_volume** | **float** | The max money volume that can be involved into transfer | [optional] [default to 10.0]
**observers** | **list[str]** | List of opportunity observers names | [optional] 
**refresh_rate** | **int** | Update rate in seconds of the arbiter&#39;s main loop | [optional] [default to 20]
**report_queue** | **str** | The name of the response queue | [optional] [default to 'arbitrage_watcher']


## Adding new markets and observers

To plug-in the new implementation of the market or observer you need to inherit their base classes:

 - `arbitrage.markets.market.MarketBase`
 - `arbitrage.observers.observer.ObserverBase`

and then add an import of the python module with the class
implementation to one of the markets or observer packages:

 - `arbitrage.markets.__init__.py`
 - `arbitrage.observers.__init__.py`
