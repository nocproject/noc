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
SITECUSTOMIZE_PATH = "lib/python%d.%d/site-packages/sitecustomize.py" % (
    VERSION[0], VERSION[1])
SITE_PATH = "lib/python%d.%d/site.py" % (VERSION[0], VERSION[1])

DATA = """import sys
sys.setdefaultencoding("utf-8")
"""


def install_sitecustomize():
    if os.path.isfile(SITECUSTOMIZE_PATH):
        return 0
    print "Installing %s" % SITECUSTOMIZE_PATH
    with open(SITECUSTOMIZE_PATH, "w") as f:
        f.write(DATA)
    return 0


def update_site():
    if not os.path.isfile(SITE_PATH):
        return 0
    with open(SITE_PATH) as f:
        data = f.read()
    if 'encoding = "ascii"' in data:
        data = data.replace('encoding = "ascii"', 'encoding = "utf-8"')
        print "Setting encoding in %s" % SITE_PATH
        with open(SITE_PATH, "w") as f:
            f.write(data)
    return 0


def main():
    r = 0
    r += install_sitecustomize()
    r += update_site()
    return r

if __name__ == "__main__":
    sys.exit(main())
