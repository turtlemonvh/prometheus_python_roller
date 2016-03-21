import unittest

from prometheus_client import Histogram, REGISTRY
from prometheus_roller import HistogramRoller


class TestHistogram(unittest.TestCase):
    def setUp(self):
        pass

    def initialize_test(self):
        """Pass in an initialized Histogram
        Check that gauges are registered
        """

        # Create histogram object
        h = Histogram('test_value', 'Testing roller')

        # Create roller from histogram
        roller = HistogramRoller(h)


        n_buckets = 0
        for m in REGISTRY.collect():
            if m.name == 'test_value':
                for name, labels, val in m.samples:
                    if name.endswith('_bucket'):
                        n_buckets += 1

        n_created_guages = 0
        for m in REGISTRY.collect():
            if m.name.endswith("_roller") and m.type == 'gauge':
                n_created_guages += 1

        # Check that expected rolled bucket gauges exist
        self.assertEqual(n_buckets, n_buckets)

        # Get values
        roller.collect()

        # Check that roller values are the same as the histogram values
        for m in REGISTRY.collect():
            for sample in m.samples:
                print sample

        #self.assertEqual(1,2)