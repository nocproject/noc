# -*- coding: utf-8 -*-
<<<<<<< HEAD
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

=======
##----------------------------------------------------------------------
## Various conversions
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
import math
##
## dBm to mW
## mW = 10^(dBm/10)
##
def dbm2mw(v):
    """
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    >>> dbm2mw(0)
    1.0
    >>> dbm2mw(10)
    10.0
    """
<<<<<<< HEAD
    return math.pow(10, v / 10)


def mw2dbm(v):
    """
    mW to dBm
    dBm = 10 log10 (mW)
    if v == 0.0 - math domain error

=======
    return math.pow(10,v/10)
##
## mW to dBm
## dBm = 10 log10 (mW) 
##
def mw2dbm(v):
    """
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    >>> mw2dbm(1)
    0.0
    >>> mw2dbm(10)
    10.0
    """
<<<<<<< HEAD
    return 10 * math.log10(float(v))
=======
    return 10*math.log(v,10)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
