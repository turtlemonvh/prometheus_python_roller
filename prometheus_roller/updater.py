import time
import threading
from threading import Lock
from roller import HistogramRoller, ROLLER_REGISTRY


class PrometheusRollingMetricsUpdater(threading.Thread):
    """Track a list of rolling objects, updating values every 'max_update_frequency' seconds
    """
    def __init__(self, max_update_frequency=None, **kwargs):
        super(PrometheusRollingMetricsUpdater, self).__init__()
        self.rollers = []
        self._lock = Lock()
        self.update_period = max_update_frequency or 5

    def add(self, roller):
        with self._lock:
            self.rollers.append(roller)

    def remove(self, roller):
        idx = -1
        with self._lock:
            for ir, r in enumerate(self.rollers):
                if r.name == roller.name:
                    idx = ir
            if idx >= 0:
                list.remove(idx)

    def run(self):
        while True:
            with self._lock:
                for roller in self.rollers:
                    roller.collect()
            time.sleep(self.update_period)


def start_update_daemon(updater=None, max_update_frequency=None, roller_registry=ROLLER_REGISTRY):
    """Start updating rolled metrics in daemon thread

    By default find all metrics that end in _roller and manage those
    """
    if updater is None:
        updater = PrometheusRollingMetricsUpdater(max_update_frequency)
        for roller in roller_registry.values():
            updater.add(roller)

    updater.daemon = True
    updater.start()

    return updater
