import os
from setuptools import setup

setup(
    name = "prometheus_roller",
    version = "0.0.1",
    author = "Timothy Van Heest",
    author_email = "timothy@ionic.com",
    description = ("Library for aggregating metrics from the Prometheus monitoring system's python client library."),
    license = "MIT",
    keywords = "prometheus monitoring client metrics",
    packages=['prometheus_roller'],
    test_suite="tests",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Monitoring",
    ],
)
