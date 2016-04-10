# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Varios metric converting functions
## to use in get_metrics scripts
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------


def percent(value, total):
    """
    Convert absolute and total values to percent
    """
    if total:
        return float(value) * 100.0 / float(total)
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
