# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Set up python environment
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
Set up python environment for stand-alone scripts.
Usage:

import set_env
set_env.setup(use_django=True)
"""
## Python modules
import site
import os
import sys


def setup(use_django=False):
    """
    Set up python environment for stand-alone scripts.
    Add following directories to the PYTHONPATH:
        noc/contrib/
        noc
        ..

    Set up DJANGO_SETTIONS if use_django set

    :param use_django: Set up DJANGO_SETTINGS_MODULE if set
    :type use_django: bool
    """
    # Adjust paths
    d = os.path.dirname(sys.argv[0])
    if not d:
        d = os.getcwd()
    d = os.path.realpath(os.path.join(d, ".."))
    contrib = os.path.abspath(os.path.join(d, "contrib", "lib"))
    sys.path.insert(0, contrib)
    sys.path.insert(0, os.path.abspath(os.path.join(d, "..")))
    sys.path.insert(0, d)
    # Install eggs from contrib/lib
    site.addsitedir(contrib)
    try:
        import settings  # @todo: Avoid loading twice
    except ImportError:
        sys.stderr.write("Error: Can't find file 'settings.py'."
                         "(If the file settings.py does indeed exist, "
                         "it's causing an ImportError somehow.)\n")
        sys.exit(1)
    os.environ["DJANGO_SETTINGS_MODULE"] = "noc.settings"
