import logging
from .observer import Observer


class Logger(Observer):
    def opportunity(self, tradechains):
        best_chain = sorted(tradechains, key=lambda x: x.profit)[-1]
        logging.info(str(best_chain))
        [h.flush() for h in logging.getLogger().handlers]
