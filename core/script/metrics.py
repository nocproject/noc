# ----------------------------------------------------------------------
# Various metric converting functions
# to use in get_metrics scripts
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
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
    return 100.0


def percent_usage(value, total):
    """
    Convert avail and usage values to percent
    """
    if total:
        return float(value) * 100.0 / (float(total) + float(value))
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


def diff(*args):
    """
    Returns diff of all arguments
    """
    return reduce(lambda x, y: x - y, args)


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


def scale(n, float_round=None):
    """
    High-order function to scale result to arbitrary value.

    f = scale(10)
    f(5) -> 50
    if float_round
    f = scale(0.1, 2)
    f(10) -> 10.2

    :param n: Scaling factor
    :param float_round: Number of decimal places
    :return: Callable, performing scaling
    :return: If float_round, return round value
    """

    def inner(v):
        return v * n

    def inner_round(v):
        return round(v * n, float_round)

    if float_round is not None:
        return inner_round

    return inner


def fix_range(l_left, l_right, over_value=0):
    """
    Check value in interval (l_left, l_right), if over - return over_value
    :param l_left: left endpoint
    :param l_right: right endpoint
    :param over_value: return if value over interval
    :return: Callable, performing scaling
    """

    def innner_fix_range(v):
        try:
            return v if l_right > float(v) > l_left else over_value
        except ValueError:
            return over_value

    return innner_fix_range


def convert_float(value):
    """
    Convert absolute and total values to percent
    """
    if isinstance(value, bytes):
        value = value.decode("utf-8")
    return float(value)
