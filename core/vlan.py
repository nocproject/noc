# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Various VLAN manipulation utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
# Third-party modules
import six
# NOC modules
from noc.lib.validators import is_vlan


rx_range = re.compile(r"^(\d+)\s*-\s*(\d+)$")


def has_vlan(vlan_filter, vlan):
    """
    Check VLAN is within vlan_filter
    :param vlan_filter:
    :param vlan:
    :return:
    """
    if not isinstance(vlan, six.integer_types):
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
