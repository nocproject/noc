# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Various system utils
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import os


def get_cpu_cores():
    """
    Return amount of available CPU cores
    :return: Number of CPU cores or 1
    :rtype: int
    """
    # Try to use Python 2.6+ multiprocessing
    try:
        import multiprocessing
        try:
            return multiprocessing.cpu_count()
        except NotImplementedError:
            pass
    except ImportError:
        pass
    # Try to use SC_NPROCESSORS_CONF
    try:
        return os.sysconf("SC_NPROCESSORS_CONF")
    except ValueError:
        return 1
