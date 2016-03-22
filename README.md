# Prometheus Roller [![Build Status](https://travis-ci.org/turtlemonvh/prometheus_python_roller.png?branch=master)](https://travis-ci.org/turtlemonvh/prometheus_python_roller)

This is a small helper utility for creating time-boxed rollups for histogram and counter metrics created using the [prometheus python client](https://github.com/prometheus/client_python).

Metrics like counters and histograms increase indefinitely, but you usually care about recent activity.  This library provides a way to turn a counter or histogram into a gauge or set of gauges that give instantaneous measures of the state of the application.

This isn't very useful if you're using [the prometheus server](https://github.com/prometheus/prometheus) since it provides [functions to do that for you](https://prometheus.io/docs/querying/functions/), but if you are sending metrics to multiple places (e.g. [check_mk](https://mathias-kettner.de/checkmk_localchecks.html)) and you want to send those metrics in a form that make basic alerting and reporting easier, this may help.

## Usage

    from prometheus_client import Histogram, Counter
    from prometheus_roller import HistogramRoller, CounterRoller, start_update_daemon

    # Create a histogram
    h = Histogram('test_value', 'Testing roller')

    # Create a counter
    c = Counter('test_counted_value', 'Testing roller')

    # Create a roller for the histogram, which calculates windowed values.
    # By default it will create a gauge with a label for each histogram bin.
    # The value of each gauge will be the change in value over the last 5 minutes, updated every 5 seconds.
    # See the `options` parameter for more configuration options.
    rh = HistogramRoller(h)

    # Create a roller for the counter, which calculates windowed values.
    # The value of each gauge will be the change in value over the last 5 minutes, updated every 5 seconds.
    # See the `options` parameter for more configuration options.
    rc = CounterRoller(c)

    # Launch a daemon thread tracking and updating all roller objects.
    # See the code for more options for configuring this update process.
    start_update_daemon()


## Installation

    # Install with pip
    pip install prometheus_roller

    # To install as editable to work on it
    pip install -e git+https://github.com/turtlemonvh/prometheus_python_roller.git#egg=prometheus_python_roller
    # OR
    git clone git@github.com:turtlemonvh/prometheus_python_roller.git prometheus-roller
    cd prometheus-roller
    python setup.py develop


## Running tests

    # Plain old python
    python -m unittest discover

    # If you have nose and coverage installed
    nosetests --with-cover


## TODO

* Add IQR reducer
* Tag version and upload to pypi


