# ----------------------------------------------------------------------
# Deep copy methods
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Any, Dict


def deep_copy(t: Dict[Any, Any]) -> Dict[Any, Any]:
    """
    Returns copy of dict `t`, following nested dict structures.
    :param t: Input dictionary
    :returns: Copied dictionary
    """
    r = {}
    for k, v in t.items():
        if isinstance(v, dict):
            r[k] = deep_copy(v)
        else:
            r[k] = v
    return r


def deep_merge(t: Dict[Any, Any], d: Dict[Any, Any]) -> Dict[Any, Any]:
    """
    Merge contents of dicts `t` and `d`, including nested dicts,
    and returns merged dict. Values from `d` override values from `t`

    :param t: Input dict
    :param d: Input dict
    :returns: Merged dict
    """

    def _merge(x: Dict[Any, Any], y: Dict[Any, Any]) -> None:
        for k, v in y.items():
            if isinstance(v, dict):
                x[k] = x.get(k, {})
                _merge(x[k], v)
            else:
                x[k] = v

    if not isinstance(t, dict) or not isinstance(d, dict):
        raise ValueError("dict required")
    r = deep_copy(t)
    _merge(r, d)
    return r
