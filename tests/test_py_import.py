# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Test python module loading
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import subprocess
import os
## Third-party modules
from nose2.tools import params


def iter_py_modules():
    """
    Enumarate all python modules
    """
    r = subprocess.Popen(
        ["./bin/hg", "locate", "*.py"],
        stdout=subprocess.PIPE
    )
    for l in r.stdout:
        yield l.strip()


@params(*tuple(iter_py_modules()))
def test_py_import(path):
    """ Load python module """
    p = path[:-3].split(os.sep)
    if p[-1] == "__init__":
        p.pop(-1)
    mn = "noc.%s" % ".".join(p)
    m = __import__(mn, {}, {}, "*")
    assert m
