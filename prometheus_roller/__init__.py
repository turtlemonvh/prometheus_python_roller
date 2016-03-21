#!/usr/bin/python

from . import roller
from . import updater

# e.g.
# https://github.com/prometheus/client_python/blob/master/prometheus_client/__init__.py

HistogramRoller = roller.HistogramRoller

start_update_daemon = updater.start_update_daemon
