# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Performance metrics
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""
Performance metrics if auto-created on demand.
Usage:

   ...
   from noc.core.perf import metrics

   metrics["my_metric1"] += 1
   metrics["my_metric2"] = 2
"""
# Python modules
from collections import defaultdict
# Third-party modules
from atomiclong import AtomicLong
import six

#
# Performance metrics
#
metrics = defaultdict(lambda: AtomicLong(0))


def apply_metrics(d):
    """
    Apply metrics value to dictionary d
    :param d: Dictionary
    :return:
    """
    for k, v in six.iteritems(metrics):
        if isinstance(v, AtomicLong):
            v = v.value
        d[k] = v
    return d
