import unittest

from prometheus_client import Histogram, REGISTRY, CollectorRegistry
from prometheus_roller import HistogramRoller, start_update_daemon, PrometheusRollingMetricsUpdater
from prometheus_roller.updater import MAX_WAIT_PERIOD


class TestRollingUpdater(unittest.TestCase):

    def setUp(self):
        self.registry = CollectorRegistry()
        self.roller_registry = {}

    def test_initialize(self):
        h_a = Histogram('test_value_a', 'Testing roller a', registry=self.registry)
        h_b = Histogram('test_value_b', 'Testing roller b', registry=self.registry)

        r_a = HistogramRoller(h_a, registry=self.registry, roller_registry=self.roller_registry)
        r_b = HistogramRoller(h_b, registry=self.registry, roller_registry=self.roller_registry)

        t = start_update_daemon(roller_registry=self.roller_registry)

        self.assertEqual(len(t.rollers), 2)

    def test_wait_period(self):
        h_a = Histogram('test_value_a', 'Testing roller a', registry=self.registry)
        h_b = Histogram('test_value_b', 'Testing roller b', registry=self.registry)
        h_c = Histogram('test_value_c', 'Testing roller c', registry=self.registry)

        r_a = HistogramRoller(h_a, registry=self.registry, roller_registry=self.roller_registry)
        r_b = HistogramRoller(h_b, registry=self.registry, roller_registry=self.roller_registry, options={
            'update_seconds': 10
        })
        r_c = HistogramRoller(h_c, registry=self.registry, roller_registry=self.roller_registry, options={
            'update_seconds': 2   
        })


        t = PrometheusRollingMetricsUpdater()

        self.assertEqual(len(t.rollers), 0)
        self.assertEqual(t.wait_period, MAX_WAIT_PERIOD)

        t.add(r_a)
        self.assertEqual(len(t.rollers), 1)
        self.assertEqual(t.wait_period, 5)

        t.add(r_b)
        self.assertEqual(len(t.rollers), 2)
        self.assertEqual(t.wait_period, 5)

        t.add(r_c)
        self.assertEqual(len(t.rollers), 3)
        self.assertEqual(t.wait_period, 1)

        t.remove(r_a)
        self.assertEqual(len(t.rollers), 2)
        self.assertEqual(t.wait_period, 2)


if __name__ == '__main__':
    unittest.main()


