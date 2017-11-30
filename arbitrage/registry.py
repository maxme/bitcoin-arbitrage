"""
The Registry of the self-pluggable markets and observers classes

To plug-in the new implementation of the market or observer
you need to inherit their base classes:

 - arbitrage.markets.market.MarketBase
 - arbitrage.observers.observer.ObserverBase

and then add an import of the python module with the class
implementation to one of the markets or observer packages:

 - arbitrage.markets.__init__.py
 - arbitrage.observers.__init__.py

As result, the implementation will be plug-in into one of
the registries below.

"""

markets_registry = {}
observers_registry = {}
