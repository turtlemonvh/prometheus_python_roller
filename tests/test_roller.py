import unittest

from prometheus_client import Histogram, REGISTRY, CollectorRegistry
from prometheus_roller import HistogramRoller, start_update_daemon


class TestRollingUpdater(unittest.TestCase):
    def setUp(self):
        self.registry = CollectorRegistry()
        self.roller_registry = {}


    def test_initialize(self):
        h_a = Histogram('test_value_a', 'Testing roller a', registry=self.registry)
        h_b = Histogram('test_value_b', 'Testing roller b', registry=self.registry)

        rr = dict()
        r_a = HistogramRoller(h_a, registry=self.registry, roller_registry=self.roller_registry)
        r_b = HistogramRoller(h_b, registry=self.registry, roller_registry=self.roller_registry)


        t = start_update_daemon(roller_registry=self.roller_registry)

        self.assertEqual(len(t.rollers), 2)

