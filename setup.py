import os
import codecs
from setuptools import setup

BASE_PATH = os.path.abspath(os.path.dirname(__file__))
with codecs.open(os.path.join(BASE_PATH, 'README.md'), 'r') as f:
    long_description = f.read()

setup(
    name = "prometheus_roller",
    version = "0.0.2",
    author = "Timothy Van Heest",
    author_email = "timothy@ionic.com",
    description = ("Library for aggregating metrics from the Prometheus monitoring system's python client library."),
    long_description=long_description,
    license = "MIT",
    keywords = "prometheus monitoring client metrics",
    url = "https://github.com/turtlemonvh/prometheus_python_roller",
    packages=['prometheus_roller'],
    install_requires=['prometheus_client'],
    test_suite="tests",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Monitoring",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5"
    ],
)
