import abc


class Observer(object, metaclass=abc.ABCMeta):
    def begin_opportunity_finder(self, depths):
        pass

    def end_opportunity_finder(self):
        pass

    def shutdown(self):
        pass

    ## abstract
    @abc.abstractmethod
    def opportunity(self, tradechains):
        pass
