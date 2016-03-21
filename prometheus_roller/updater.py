import time
import threading
from threading import Lock
from fractions import gcd
from roller import HistogramRoller, ROLLER_REGISTRY

# Don't wait longer than every 30 seconds in between checks
MAX_WAIT_PERIOD = 30


class PrometheusRollingMetricsUpdater(threading.Thread):
    """Track a list of rolling objects, updating values every 'max_update_frequency' seconds
    """
    def __init__(self, **kwargs):
        super(PrometheusRollingMetricsUpdater, self).__init__()
        self.rollers = []
        self._lock = Lock()

        # The smallest time to wait between checks
        self.update_wait_period()

    def update_wait_period(self):
        """Calculate the longest interval we can wait.
        """
        periods = map(lambda r: r.update_seconds, self.rollers)
        if len(periods):
            self.wait_period = min(reduce(gcd, periods), MAX_WAIT_PERIOD)
        else:
            self.wait_period = MAX_WAIT_PERIOD

        return self.wait_period

    def add(self, roller):
        with self._lock:
            self.rollers.append(roller)
            self.update_wait_period()

    def remove(self, roller):
        idx = -1
        with self._lock:
            for ir, r in enumerate(self.rollers):
                if r.name == roller.name:
                    idx = ir
            if idx >= 0:
                self.rollers.pop(idx)
            self.update_wait_period()

    def run(self):
        while True:
            # Sleep until next period
            time.sleep(time.time() % self.wait_period)

            now_second = int(time.time())
            with self._lock:
                for roller in self.rollers:
                    if now_second % roller.update_seconds == 0:
                        roller.collect()


def start_update_daemon(updater=None, roller_registry=ROLLER_REGISTRY):
    """Start updating rolled metrics in daemon thread
    """
    if updater is None:
        updater = PrometheusRollingMetricsUpdater()
        for roller in roller_registry.values():
            updater.add(roller)

    updater.daemon = True
    updater.start()

    return updater
