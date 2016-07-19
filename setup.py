#!/usr/bin/env python

from setuptools import setup
import sys


if sys.version_info < (3,):
    print("bitcoin-arbitrage requires Python version >= 3.0")
    sys.exit(1)

setup(name='bitcoin-arbitrage',
      packages = ["arbitrage"],
      version='0.2',
      description='Bitcoin arbitrage opportunity watcher',
      author='Phil Song',
      author_email='songbohr@gmail.com',
      url='https://github.com/philsong/bitcoin-arbitrage',
      arbitrage=['bin/bitcoin-arbitrage'],
      test_suite='nose.collector',
      tests_require=['nose'],
  )
