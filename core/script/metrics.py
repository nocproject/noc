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
