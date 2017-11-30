import time
import logging
from multiprocessing import Process, Value
from threading import Lock

from arbitrage.arbiter import Arbiter
from arbitrage.config import Configuration

LOG = logging.getLogger(__name__)


class ServiceException(Exception):
    pass


class ArbiterService(object):
    """Represents the service of arbiter process management"""

    def __init__(self):
        self.arbiter = None
        self.arbiter_process = None
        self.arbiter_stop_flag = Value('b', False)
        self.config = Configuration()
        self.start_time = 0
        self.lock = Lock()

    @staticmethod
    def _loop(arbiter, is_stop):
        """Arbiter worker process main loop"""
        while not is_stop.value:
            try:
                arbiter.depths = arbiter.update_depths()
                arbiter.tickers()
                arbiter.tick()
                time.sleep(arbiter.config.refresh_rate)
            except Exception:
                LOG.exception('Update iteration failed')
        is_stop.value = True
        LOG.info('Exit from arbiter loop')

    def status(self):
        """Return status of the arbiter's worker process"""
        with self.lock:
            started = False
            if self.arbiter and not self.arbiter_stop_flag.value:
                started = True
            started = started and self.arbiter_process.is_alive()
            return {
                'is_started': started,
                'last_start_time': self.start_time,
                'current_parameters': self.config.as_dict()
            }

    def start(self, config: dict):
        """Start the arbiter worker process"""
        with self.lock:
            if self.arbiter and not self.arbiter_stop_flag.value:
                msg = 'Failed to start. Arbiter process already running.'
                raise ServiceException(msg)

            if self.arbiter_process and self.arbiter_process.is_alive():
                LOG.info('Arbiter process is still alive. Terminating...')
                self.arbiter_process.terminate()

            self.arbiter_stop_flag = Value('b', False)
            self.config = Configuration().update(config)
            self.arbiter = Arbiter(self.config)
            self.arbiter_process = Process(target=self._loop,
                                           args=(self.arbiter,
                                                 self.arbiter_stop_flag))
            self.arbiter_process.daemon = True
            self.arbiter_process.start()
            self.start_time = time.time()
            LOG.info('Arbiter process was started')
            return True

    def stop(self):
        """Stop the arbiter worker process"""
        with self.lock:
            is_stopped = True
            if self.arbiter:
                self.arbiter_stop_flag.value = True
                if self.arbiter_process.is_alive():
                    self.arbiter_process.terminate()
                    is_stopped = not self.arbiter_process.is_alive()
            if is_stopped:
                LOG.info('Arbiter process was stopped')
            return is_stopped
