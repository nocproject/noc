# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Russian address formating and parsing utilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.comp import smart_text


div_norm = {"село": "с", "поселок": "п", "город": "г", "поселок городского типа": "пгт"}

rx_div_start = re.compile(
    "^([дсгхуп]|пгт|село|сельсовет|поселок городского типа|поселок|город|ст-ца|муниципальный округ|сдт|рп) (.+)$",
    re.UNICODE,
)
rx_div_end = re.compile("^(.+) (сельсовет|муниципальный район|муниципальный округ)$", re.UNICODE)


def normalize_division(s):
    """
    Normalize division and split short name
    :returns: (short name, name)
    """
    if isinstance(s, str):
        s = smart_text(s)
    match = rx_div_start.match(s)
    if match:
        sn, n = match.groups()
        return div_norm.get(sn, sn), n
    match = rx_div_end.search(s)
    if match:
        n, sn = match.groups()
        return sn, n
    return None, s
