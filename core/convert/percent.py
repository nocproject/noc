# ---------------------------------------------------------------------
# Various conversions
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from typing import Optional


def normalize_percent(v):
    """
    Scalar to Percent
    mW = 10^(dBm/10)

    >>> normalize_percent(0.0)
    0.0
    >>> normalize_percent(-1.0)
    0.0
    >>> normalize_percent(0.34)
    0.34
    >>> normalize_percent(103)
    100.0
    """
    return float(max(0, min(v, 100)))


def normalize_range(v, min_value: Optional[float] = None, max_value: Optional[float] = None):
    """
    Scalar to Percent
    mW = 10^(dBm/10)

    >>> normalize_range(0.0, 0.0, 100.0)
    0.0
    >>> normalize_range(-1.0, 0.0, 100.0)
    0.0
    >>> normalize_range(0.34, 0.0, 1.0)
    0.34
    >>> normalize_range(103, 0.0, 100.0)
    100.0
    >>> normalize_range(103, 0.0)
    103.0
    """
    if min_value is not None:
        v = max(min_value, v)
    if max_value is not None:
        v = min(max_value, v)
    return float(v)
