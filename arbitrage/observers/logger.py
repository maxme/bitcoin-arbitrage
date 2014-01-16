import logging
from .observer import Observer


class Logger(Observer):
    def opportunity(self, tradechains):
        best_chain = sorted(tradechains, key=lambda x: x.profit)[-1]
        if logging.root.isEnabledFor(logging.DEBUG):
            for chain in tradechains:
                logging.debug(str(chain))
        else:
            logging.info(str(best_chain))
        [h.flush() for h in logging.getLogger().handlers]
