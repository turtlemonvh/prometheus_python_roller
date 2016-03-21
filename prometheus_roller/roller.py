import datetime
from collections import deque
from prometheus_client import Gauge, REGISTRY

# Keep track of rollers created by the user to make it simpler to use
ROLLER_REGISTRY = dict()


class HistogramRoller(object):
    """Accepts a Histogram object and creates gauges tracking metrics over a given time period for that bucket.

    Keep a rolling list of recent values on the gauge object to make roll ups easy
    """
    def __init__(self, histogram, options={}, registry=REGISTRY, roller_registry=ROLLER_REGISTRY):
        self.hist = histogram

        # Extract options
        self.name = options.get('name')
        self.documentation = options.get('documentation')
        self.retention_seconds = options.get('retention_seconds', 5*60) # Last 5 minutes

        self.retention_td = datetime.timedelta(seconds=5*60)

        # Keys are 'le' values
        # Holds dequeus containing values for each gauge
        self.past_gauge_values = dict()

        generated_name = ""
        full_name = ""
        for full_name, labels, value in self.iter_hist_buckets():
            le_label = labels['le']
            self.past_gauge_values[le_label] = deque()
            generated_name = full_name[:-7] + '_gauge_rolled'

        self.name = self.name or generated_name
        self.documentation = self.documentation or 'Tracks the recent behavior of %s' % (full_name[0:-7])

        # A single top level gauge with bucket labels tracks the values
        self.gauge = Gauge(
            self.name,
            self.documentation,
            labelnames=('le',), 
            registry=registry
        )

        roller_registry[self.name] = self

    def iter_hist_buckets(self):
        # (u'test_value_bucket', {u'le': '0.005'}, 0.0)
        # (u'test_value_count', {}, 0.0)
        for full_name, labels, value in self.hist.collect()[0].samples:
            if full_name.endswith("_bucket"):
                yield full_name, labels, value

    def collect(self):
        """Collect should only be called about every second, not in a tight loop.

        FIXME: Add a lock?
        """
        now = datetime.datetime.now()
        for full_name, labels, value in self.iter_hist_buckets():
            sample_key = labels['le']

            # Add value
            self.past_gauge_values[sample_key].append((now, value))

            # Drop old values
            oldest_allowed = now - self.retention_td
            while len(self.past_gauge_values[sample_key]):
                date_added, _ = self.past_gauge_values[sample_key][0]
                if date_added < oldest_allowed:
                    self.past_gauge_values[sample_key].popleft()
                else:
                    break

            # Average existing values
            total = 0
            ct = 0
            for _, val in self.past_gauge_values[sample_key]:
                total += val
                ct += 1

            self.gauge.labels({'le': sample_key}).set(total/ct)


