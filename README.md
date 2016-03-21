# Prometheus Roller

A small helper utility for creating time-boxed rollups for prometheus metrics.

Metrics like counters and histograms usually increase indefinitely, but you usually care about recent activity.  This library provides a way to turn a counter or histogram into set of gauges that give instantaneous measures of the state of the application.

## Usage

    h = Histogram('test_value', 'Testing roller')
    r = HistogramRoller(h)

## Installation

    # With pip
    pip install git+https://github.com/turtlemonvh/prometheus_python_roller.git#egg=prometheus_python_roller

    # To install locally and work on it
    python setup.py develop

## Tests

    python -m unittest discover


## TODO

Add function to find all 'rollers' and manage them in daemon thread

Add options

Add better tests

Make pip installable

Several types of roll ups

* moving averages
* rates
* IQRs
* max-over-period values

## Author

Timothy Van Heest

## License

MIT
