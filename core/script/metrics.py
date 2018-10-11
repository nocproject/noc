# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Various metric converting functions
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
        v = (float(total) - float(value)) * 100.0 / float(total)
        if v >= 0.0:
            return v
    return 100.0


def convert_percent_str(x):
    """
    Convert 09% to 9.0 value
    Convert 09 to 9.0 value
    If x = None, return 0
    """
    if x:
        return float(str(x).strip("% "))
    return 0


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


def scale(n):
    """
    High-order function to scale result to arbitrary value.

    f = scale(10)
    f(5) -> 50

    :param x: Scaling factor
    :return: Callable, performing scaling
    """
    def inner(v):
        return v * n

    return inner
