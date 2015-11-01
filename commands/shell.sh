#!/bin/sh
if [ -x ./bin/ipython ]; then
    exec ./bin/ipython
fi
./bin/python
