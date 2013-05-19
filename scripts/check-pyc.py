#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Check for hanging *.pyc files
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import sys
## NOC modules
from noc.settings import INSTALLED_APPS


def check():
    # Check for hanging *.pyc
    r = []
    for app in INSTALLED_APPS:
        if not app.startswith("noc."):
            continue
        app = app[4:]
        for root, dirs, files in os.walk(app):
            # .pyc present, .py absent
            py = set(f + "c" for f in files if f.endswith(".py"))
            pyc = set(f for f in files if f.endswith(".pyc"))
            left = pyc - py
            if left:
                r += [os.path.join(root, f) for f in left]
    if r:
        # Try to remote hanging *.pyc
        rr = []
        for f in r:
            try:
                os.unlink(f)
            except OSError:
                rr += [f]
        if rr:
            sys.stderr.write("Error: hanging .pyc files found:\n")
            sys.stderr.write("    " + "\n    ".join(rr) + "\n")
            sys.stderr.write("Remove them manually and restart post-update")
            return 1
    return 0

if __name__ == "__main__":
    sys.exit(check())
