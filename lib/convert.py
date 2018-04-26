# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Various conversions
# ---------------------------------------------------------------------
# Copyright (C) 2007-2010 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
import math


def dbm2mw(v):
    """
    dBm to mW
    mW = 10^(dBm/10)

    >>> dbm2mw(0)
    1.0
    >>> dbm2mw(10)
    10.0
    """
    return math.pow(10, v / 10)


def mw2dbm(v):
    """
    mW to dBm
    dBm = 10 log10 (mW)
    if v == 0.0 - math domain error

    >>> mw2dbm(1)
    0.0
    >>> mw2dbm(10)
    10.0
    """
    return 10 * math.log10(float(v))
