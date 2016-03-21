# Prometheus Roller

A small helper utility for creating time-boxed rollups for prometheus metrics.

Metrics like counters and histograms usually increase indefinitely, but you usually care about recent activity.  This library provides a way to turn a counter or histogram into set of gauges that give instantaneous measures of the state of the application.

## Usage

    from prometheus_client import Histogram
    from prometheus_roller import HistogramRoller, start_update_daemon

    # Create a histogram
    h = Histogram('test_value', 'Testing roller')

    # Create a roller for this histogram, which calculates windowed values
    # By default it will create a gauge with a label for each histogram bin
    # The value of each gauge will be the change in value over the last 5 minutes, calculated every 5 seconds
    # See the `options` parameter for more configuration options
    r = HistogramRoller(h)

    # Launch a daemon thread tracking and updating all roller objects
    # See the code for more options for configuring this update process
    start_update_daemon()

## Installation

    # With pip
    pip install git+https://github.com/turtlemonvh/prometheus_python_roller.git#egg=prometheus_python_roller

    # To install locally and work on it
    python setup.py develop

## Tests

    python -m unittest discover

## TODO

* Add IQR reducer