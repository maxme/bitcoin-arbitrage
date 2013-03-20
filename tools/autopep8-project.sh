#!/bin/sh
find . -name "*.py" | xargs autopep8 -i --max-line-length=119

