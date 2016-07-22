#!/bin/sh
if [ -x /usr/bin/ipython ]; then
    exec /usr/bin/env ipython
fi
/usr/bin/env python
