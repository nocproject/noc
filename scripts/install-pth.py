#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Install noc.pth file
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

import sys
import os


def find_site_packages():
    return [p for p in sys.path if p.endswith("site-packages")][-1]


def get_pth():
    cwd = os.path.abspath(os.getcwd())
    upd = os.path.abspath(os.path.join(cwd, ".."))

    return "\n".join([
        "# NOC paths",
        "import os; os.environ['DJANGO_SETTINGS_MODULE'] = 'noc.settings'",
        cwd,
        upd
    ])


def write_pth():
    pth = os.path.join(find_site_packages(), "noc.pth")
    f = open(pth, "w")
    f.write(get_pth())
    f.close()

if __name__ == "__main__":
    write_pth()
