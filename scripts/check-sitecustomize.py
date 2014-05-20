#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Check and install sitecustomize.py
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import sys
import os

VERSION = sys.version_info
PATH = "lib/python%d.%d/site-packages/sitecustomize.py" % (
    VERSION[0], VERSION[1])
DATA = """import sys
sys.setdefaultencoding("utf-8")
"""


def main():
    if os.path.isfile(PATH):
        return 0
    print "Installing %s" % PATH
    with open(PATH, "w") as f:
        f.write(DATA)
    return 0

if __name__ == "__main__":
    sys.exit(main())
