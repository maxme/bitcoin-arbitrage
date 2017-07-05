import abc
from arbitrage.registry import observers_registry


class Plugin(abc.ABCMeta):
    """Dynamically add a class to the registry"""

    def __new__(mcs, clsname, bases, attrs):
        newclass = super(Plugin, mcs).__new__(mcs, clsname, bases, attrs)
        if not clsname.endswith('Base'):
            observers_registry[clsname] = newclass
        return newclass


class ObserverBase(object, metaclass=Plugin):
    """"""

    def __init__(self, config):
        self.config = config

    def begin_opportunity_finder(self, depths):
        pass

    def end_opportunity_finder(self):
        pass

    @abc.abstractmethod
    def opportunity(self, profit, volume, buyprice, kask, sellprice,
                    kbid, perc, weighted_buyprice, weighted_sellprice):
        pass
