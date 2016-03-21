import datetime
from collections import deque
from prometheus_client import Gauge, REGISTRY

# Keep track of rollers created by the user to make it simpler to use
ROLLER_REGISTRY = dict()


##########
# Utility
##########

def iter_hist_buckets(hist):
    """Generator that returns buckets for a histogram"""
    for full_name, labels, value in hist.collect()[0].samples:
        if full_name.endswith("_bucket"):
            yield full_name, labels, value

def remove_old_values(past_values, oldest_time):
    while len(past_values):
        date_added, _ = past_values[0]
        if date_added < oldest_time:
            v = past_values.popleft()
        else:
            break

def values_to_deltas(past_values):
    """Turn a deque holding past gauge values into a list of deltas.
    These should be evenly distributed in time
    """
    deltas = []
    prev_val = None
    for (ival, (_, val)) in enumerate(past_values):
        if ival > 0:
            deltas.append(val - prev_val)
        prev_val = val
    return deltas

##########
# Reducers
##########

## This is the default, and usually what you want

# Sum of changes over period
def sum_total(deltas, **kwargs):
    total = 0.0
    for val in deltas:
        total += val
    return total

## Other methods are useful for quickly changing values where most deltas >> 0

# Average change
def average(deltas, **kwargs):
    total = 0.0
    ct = 0.0
    for val in deltas:
        total += val
        ct += 1
    if ct > 0:
        return total/ct
    return 0.0

# Exponential moving average of the delta
def ema(deltas, **kwargs):
    alpha = kwargs.get('alpha', 0.5)
    s = 0.0
    for (ival, val) in enumerate(deltas):
        if ival == 0:
            s = val
        else:
            s = alpha*val + (1-alpha)*s

    return s

# Max delta
def max_value(deltas, **kwargs):
    max_val = float('-inf')
    for val in deltas:
        if val > max_val:
            max_val = val
    return max_val

# Min delta
def min_value(deltas, **kwargs):
    min_val = float('inf')
    for val in deltas:
        if val < min_val:
            min_val = val
    return min_val


REDUCERS = {
    'sum': sum_total,
    'avg': average,
    'max': max_value, 
    'min': min_value,
    'ema': ema
}


##########
# Rollers
##########

DEFAULT_UPDATE_PERIOD = 5           # every 5 seconds
DEFAULT_RETENTION_PERIOD = 5*60     # last 5 minutes

class HistogramRoller(object):
    """Accepts a Histogram object and creates gauges tracking metrics over a given time period for that bucket.
    """
    def __init__(self, histogram, options={}, registry=REGISTRY, roller_registry=ROLLER_REGISTRY):
        self.hist = histogram

        # Extract options

        # Name and documentation are generated if not passed
        self.name = options.get('name')
        self.documentation = options.get('documentation')
        self.retention_seconds = options.get('retention_seconds', DEFAULT_RETENTION_PERIOD)
        self.update_seconds = options.get('update_seconds', DEFAULT_UPDATE_PERIOD)

        if self.update_seconds % 1 != 0:
            raise ValueError("'update_seconds' must be a multiple of 1")

        # By default, values are differences over a fixed window
        self.reducer_choice = options.get('reducer', 'sum')
        self.reducer_kwargs = options.get('reducer_kwargs', {})
        self.retention_td = datetime.timedelta(seconds=self.retention_seconds)

        # 'reducer_choice' can be a function that accepts a list of float deltas and returns a float
        if hasattr(self.reducer_choice, '__call__'):
            self.reducer = self.reducer_choice
        else:
            self.reducer = REDUCERS[self.reducer_choice]

        # Keys are 'le' values
        # Holds deques containing values for each gauge
        self.past_values = dict()

        generated_name = ""
        full_name = ""
        for full_name, labels, value in iter_hist_buckets(self.hist):
            le_label = labels['le']
            self.past_values[le_label] = deque()

        generated_name = full_name[:-7] + '_%s_rolled' % (self.reducer_choice)
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

    def collect(self):
        """Loop over current histogram bucket values and update gauges.

        Usage:
        * Collect should only be called about every second, not in a tight loop.
        * Should only be called in 1 thread at a time.
        """
        now = datetime.datetime.now()
        for full_name, labels, value in iter_hist_buckets(self.hist):
            sample_key = labels['le']

            # Add value
            self.past_values[sample_key].append((now, value))

            # Drop old values
            remove_old_values(self.past_values[sample_key], now - self.retention_td)

            # Calculate and record new rolled value
            v = self.reducer(values_to_deltas(self.past_values[sample_key]), **self.reducer_kwargs)
            self.gauge.labels({'le': sample_key}).set(v)



