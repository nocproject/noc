#!/bin/sh
source ./commands/base.sh

if [ ! -d ".ipython" ]; then
    mkdir .ipython || error_exit "Cannot create .ipython directory"
fi
exec ./bin/ipython notebook --notebook-dir=.ipython
