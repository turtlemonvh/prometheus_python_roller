from __future__ import division, print_function

import time
import threading
from threading import Lock
from fractions import gcd
from .roller import ROLLER_REGISTRY

# Don't wait longer than every 30 seconds in between checks
MAX_WAIT_PERIOD = 30


class PrometheusRollingMetricsUpdater(threading.Thread):
    """Thread used to periodically update a list of roller objects.
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
        periods = [r.update_seconds for r in self.rollers]
        if len(periods):
            for iperiod, period in enumerate(periods):
                if iperiod == 0:
                    self.wait_period = period
                else:
                    self.wait_period = gcd(period, self.wait_period)
            self.wait_period = min(self.wait_period, MAX_WAIT_PERIOD)
        else:
            self.wait_period = MAX_WAIT_PERIOD

        return self.wait_period

    def add(self, roller):
        """Add a new roller to track.
        """
        with self._lock:
            self.rollers.append(roller)
            self.update_wait_period()

    def remove(self, roller):
        """Stop tracking a roller.
        """
        idx = -1
        with self._lock:
            for ir, r in enumerate(self.rollers):
                if r.name == roller.name:
                    idx = ir
            if idx >= 0:
                self.rollers.pop(idx)
            self.update_wait_period()

    def run(self):
        """Run forever, executing any updates that need to take place and then sleeping
        until the next update time.
        """
        while True:
            now_second = int(time.time())
            with self._lock:
                for roller in self.rollers:
                    if now_second % roller.update_seconds == 0:
                        roller.collect()

            # Sleep until next period
            time.sleep(self.wait_period - time.time() % self.wait_period)


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
