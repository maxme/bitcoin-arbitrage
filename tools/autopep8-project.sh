#!/bin/sh
find . -name "*.py" -or -name "config.py-example" | xargs autopep8 -i --max-line-length=119

