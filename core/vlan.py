# ----------------------------------------------------------------------
# Various VLAN manipulation utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.validators import is_vlan

rx_range = re.compile(r"^(\d+)\s*-\s*(\d+)$")


def has_vlan(vlan_filter, vlan):
    """
    Check VLAN is within vlan_filter
    :param vlan_filter:
    :param vlan:
    :return:
    """
    if not isinstance(vlan, int):
        vlan = int(vlan)
    if not is_vlan(vlan):
        return False
    for p in vlan_filter.split(","):
        p = p.strip()
        if not p:
            continue
        if "-" in p:
            # Range
            match = rx_range.match(p)
            if match:
                try:
                    f, t = [int(x) for x in match.groups()]
                    if f <= vlan <= t:
                        return True
                except ValueError:
                    pass
        else:
            # Single value
            try:
                v = int(p)
                if v == vlan:
                    return True
            except ValueError:
                pass
    return False


def optimize_filter(vlan_filter, sep=","):
    """
    Reorder and optimize vlan filter
    :param vlan_filter:
    :return:
    """

    def get_part(v):
        v = v.strip()
        if "-" in v:
            v1, v2 = [int(x) for x in v.split("-")]
            return min(v1, v2), max(v1, v2)
        return int(v), int(v)

    def iter_merge(parts):
        last = parts.pop(0)
        for n in parts:
            if last[1] >= n[0] - 1:
                last = (last[0], max(last[1], n[1]))
            else:
                yield last
                last = n
        yield last

    def fmt(p):
        f, t = p
        if f == t:
            return str(f)
        return "%d-%d" % p

    vlan_filter = vlan_filter.replace(" ", "")
    if not vlan_filter:
        return ""
    return sep.join(fmt(p) for p in iter_merge(sorted(get_part(x) for x in vlan_filter.split(","))))
