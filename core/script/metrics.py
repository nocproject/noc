# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Varios metric converting functions
# to use in get_metrics scripts
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
# Python modules
from functools import reduce


def percent(value, total):
    """
    Convert absolute and total values to percent
    """
    if total:
        return float(value) * 100.0 / float(total)
    else:
        return 100.0


def percent_usage(value, total):
    """
    Convert avail and usage values to percent
    """
    if total:
        return float(value) * 100.0 / (float(total) + float(value))
    else:
        return 100.0


def percent_invert(value, total):
    """
    Convert avail and total values to percent
    """
    if total:
        return (float(total) - float(value)) * 100.0 / float(total) if value <= total else 100.00
    else:
        return 100.0


def sum(*args):
    """
    Returns sum of all arguments
    """
    return reduce(lambda x, y: x + y, args)


def subtract(*args):
    """
    Subtract from first arguments
    """
    return args[0] - reduce(lambda x, y: x + y, args[1:])


def is1(x):
    return 1 if x == 1 else 0


def invert0(x):
    """
    Invert 0 -> 1 if OK = 0, FALSE > 1
    """
    return 0 if x > 0 else 1
