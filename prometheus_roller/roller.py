import datetime
from collections import deque
from prometheus_client import Gauge



class HistogramRoller(object):
    """
    Keep a rolling list of recent values on the gauge object to make roll ups easy

    https://github.com/prometheus/client_python/blob/master/prometheus_client/core.py#L640
    https://github.com/prometheus/client_python#custom-collectors

    Gauge Metric Family
    https://github.com/prometheus/client_python/blob/master/prometheus_client/core.py#L132
    Gauge


    Keep a deque of recent values
    Drop the oldest values when they are older than the retention period

    E.g.
    upload_seconds_bucket{le="0.005"} 168.0
    upload_seconds_bucket{le="0.01"} 168.0
    upload_seconds_bucket{le="0.025"} 168.0

    https://github.com/prometheus/client_python/blob/master/prometheus_client/exposition.py#L33
    - where metrics are displayed to the user

    https://github.com/prometheus/client_python/blob/master/prometheus_client/core.py#L48
    - iterates over all items in regsitry

    https://github.com/prometheus/client_python/blob/master/prometheus_client/core.py#L335
    - _MetricsWrapper adds a .collect() function

    Alt:
    https://en.wikipedia.org/wiki/Reservoir_sampling

    https://github.com/prometheus/client_python/blob/master/prometheus_client/core.py#L219
    _ValueClass is a float protected by a mutex, with some methods for access

    https://github.com/prometheus/client_python/blob/master/prometheus_client/core.py#L309
    _MetricsWrapper handles registration, and allows that to be configured already
    """
    def __init__(self, histogram, options=None):
        self.hist = histogram

        # Last 5 minutes
        self.retention_td = datetime.timedelta(seconds=5*60)

        # Hold gauge objects
        self.name = None

        # Keys are 'le' values
        # Holds dequeus containing values for each gauge
        self.past_gauge_values = dict()

        full_name = ""
        for full_name, labels, value in self.iter_hist_buckets():
            le_label = labels['le']
            self.past_gauge_values[le_label] = deque()
            self.name = full_name[:-7] + '_gauge_rolled'

        # A single top level gauge with some labels tracks the values
        # c = Counter('my_requests_total', 'HTTP Failures', ['method', 'endpoint'])
        self.gauge = Gauge(
            self.name,
            'Tracks the recent behavior of %s' % (full_name[0:-7]),
            labelnames=('le',), 
        )


    def iter_hist_buckets(self):
        # (u'test_value_bucket', {u'le': '0.005'}, 0.0)
        # (u'test_value_count', {}, 0.0)
        for full_name, labels, value in self.hist.collect()[0].samples:
            if full_name.endswith("_bucket"):
                yield full_name, labels, value


    def collect(self):
        """Collect should only be called about every second, not in a tight loop.
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
                total += 0
                ct += 1

            self.gauge.labels({'le': sample_key}).set(total/ct)



