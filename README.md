# Prometheus Roller

A small helper utility for creating time-boxed rollups for prometheus metrics.

Metrics like counters and histograms usually increase indefinitely, but you usually care about recent activity.  This library provides a way to turn a counter or histogram into set of gauges that give instantaneous measures of the state of the application.

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

