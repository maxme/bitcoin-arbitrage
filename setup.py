#!/usr/bin/env python

from setuptools import setup, find_packages
import sys

if sys.version_info < (3,):
    print("bitcoin-arbitrage requires Python version >= 3.0")
    sys.exit(1)

setup(name='bitcoin-arbitrage',
      packages=find_packages(),
      version='0.2',
      description='Bitcoin arbitrage opportunity watcher',
      install_requires=[
          "sleekxmpp", 'tenacity', 'pika', 'PyYAML'
      ],
      arbitrage=['bin/bitcoin-arbitrage'],
      test_suite='nose.collector',
      tests_require=['nose']
      )
