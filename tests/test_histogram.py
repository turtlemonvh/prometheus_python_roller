import unittest

import datetime
from collections import deque

from prometheus_client import Histogram, REGISTRY, CollectorRegistry
from prometheus_roller import HistogramRoller
from prometheus_roller.roller import sum_total, average, max_value, ema, remove_old_values


class TestHistogram(unittest.TestCase):

    def setUp(self):
        self.registry = CollectorRegistry()

    def get_rolled_samples(self):
        """Get all 'rolled' type gauges in the current registry
        """
        for m in self.registry.collect():
            if m.name.endswith('_rolled'):
                for name, labels, val in m.samples:
                    yield name, labels, val

    def get_hist_samples(self):
        """Get all histogram buckets in the current registry
        """
        for m in self.registry.collect():
            if m.name == 'test_value':
                for name, labels, val in m.samples:
                    if name.endswith('_bucket'):
                        yield name, labels, val

    def test_initialize(self):
        h = Histogram('test_value', 'Testing roller', registry=self.registry)
        roller = HistogramRoller(h, registry=self.registry)

        n_buckets = 0
        for name, _, _ in self.get_hist_samples():
            if name.endswith('_bucket'):
                n_buckets += 1

        n_created_guages = 0
        for _, _, _ in self.get_rolled_samples():
            n_created_guages += 1

        # Check that roller gauges don't exist until values are added
        self.assertTrue(n_buckets > 0)
        self.assertTrue(n_created_guages == 0)

        self.assertEqual(roller.name, 'test_value_sum_rolled')

    def test_collect(self):
        h = Histogram('test_value', 'Testing roller', registry=self.registry)
        roller = HistogramRoller(h, registry=self.registry)

        # Get values
        roller.collect()

        n_buckets = 0
        for _, _, _ in self.get_hist_samples():
            n_buckets += 1

        n_created_guages = 0
        for _, _, _ in self.get_rolled_samples():
            n_created_guages += 1

        self.assertTrue(n_buckets > 0)
        self.assertTrue(n_created_guages > 0)
        self.assertEqual(n_buckets, n_created_guages)

        # Check that roller values are still 0.0 after initial collection
        for name, labels, value in self.get_rolled_samples():
            self.assertEqual(value, 0.0)

        # Add some samples
        for i in range(100):
            h.observe(pow(2, i/10 - 2))

        # Collect hisogram values
        hist_values = dict()
        for name, labels, value in self.get_hist_samples():
            hist_values[labels['le']] = value

        # Make sure they are still equal after collection
        for name, labels, value in self.get_rolled_samples():
            self.assertEqual(value, 0.0)

        roller.collect()

        for name, labels, value in self.get_rolled_samples():
            self.assertEqual(value, hist_values[labels['le']])

    def test_customize_reducer(self):
        h = Histogram('test_value', 'Testing roller', registry=self.registry)
        roller_max = HistogramRoller(h, registry=self.registry, options={
            'reducer': 'max'
        })
        roller_min = HistogramRoller(h, registry=self.registry, options={
            'reducer': 'sum'
        })

        for state in [2.6, 4.7, 3.8, 2.8]:
            h.observe(state)
            roller_max.collect()
            roller_min.collect()

        # Deltas = 1, 1, 1
        nchecks = 0
        for m in self.registry.collect():
            if m.name.endswith('max_rolled'):
                for name, labels, val in m.samples:
                    if labels['le'] == '5.0':
                        nchecks += 1
                        self.assertEqual(val, 1.0)
        self.assertTrue(nchecks > 0)

        nchecks = 0
        for m in self.registry.collect():
            if m.name.endswith('sum_rolled'):
                for name, labels, val in m.samples:
                    if labels['le'] == '5.0':
                        self.assertEqual(val, 3.0)
                        nchecks += 1
        self.assertTrue(nchecks > 0)


class TestWindowing(unittest.TestCase):
    def test_basic(self):
        values = deque()
        for i in range(100):
            td = datetime.datetime.now() + datetime.timedelta(seconds=i+1-100)
            values.append((td, 10))

        cutoff_time = datetime.datetime.now() + datetime.timedelta(seconds=-50)
        remove_old_values(values, cutoff_time)

        self.assertEqual(len(values), 50)


class TestReducers(unittest.TestCase):
    def setUp(self):
        # Empty
        self.d0 = []

        # Single value
        self.d1 = []
        values = [5]
        for v in values:
            self.d1.append(v)

        # Normal case
        self.d2 = []
        values = [1, 2, 3, 3, 2, 1, 2, 3]
        for v in values:
            self.d2.append(v)

    def test_average(self):
        self.assertEqual(average(self.d0), 0.0)
        self.assertEqual(average(self.d1), 5.0)
        self.assertEqual(average(self.d2), 17.0/8)

    def test_max(self):
        self.assertEqual(max_value(self.d0), float('-inf'))
        self.assertEqual(max_value(self.d1), 5.0)
        self.assertEqual(max_value(self.d2), 3.0)

    def test_sum(self):
        self.assertEqual(sum_total(self.d0), 0.0)
        self.assertEqual(sum_total(self.d1), 5.0)
        self.assertEqual(sum_total(self.d2), 17.0)

    def test_exponential_moving_average(self):
        self.assertEqual(ema(self.d0, alpha=0.9), 0.0)
        self.assertEqual(ema(self.d1, alpha=0.9), 5.0)
        self.assertAlmostEqual(ema(self.d2, alpha=0.9), 2.89, 2)
        self.assertAlmostEqual(ema(self.d2, alpha=0.5), 2.41, 2)


if __name__ == '__main__':
    unittest.main()
