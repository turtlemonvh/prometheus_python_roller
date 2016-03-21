import unittest

from prometheus_client import Histogram, REGISTRY, CollectorRegistry
from prometheus_roller import HistogramRoller


class TestHistogram(unittest.TestCase):

    def setUp(self):
        self.registry = CollectorRegistry()

    def get_rolled_samples(self):
        """Get all 'rolled' type gauges in the current registry
        """
        for m in self.registry.collect():
            if m.name == 'test_value':
                for name, labels, val in m.samples:
                    if name.endswith('_roller') and m.type == 'gauge':
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

        # Check that expected rolled bucket gauges exist
        self.assertEqual(n_buckets, n_buckets)

        # Check that roller values are initialized to 0.0
        for name, labels, value in self.get_rolled_samples():
            self.assertEqual(value, 0.0)

    def test_collect(self):
        h = Histogram('test_value', 'Testing roller', registry=self.registry)
        roller = HistogramRoller(h, registry=self.registry)

        # Get values
        roller.collect()

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
            self.assertEqual(value, hist_values[labels['le']]/2.0)


if __name__ == '__main__':
    unittest.main()
