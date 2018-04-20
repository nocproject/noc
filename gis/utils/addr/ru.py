# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Russian address formating and parsing utilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
=======
##----------------------------------------------------------------------
## Russian address formating and parsing utilities
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
import re


div_norm = {
    u"село": u"с",
    u"поселок": u"п",
    u"город": u"г",
    u"поселок городского типа": u"пгт"
}

rx_div_start = re.compile(u"^([дсгхуп]|пгт|село|сельсовет|поселок городского типа|поселок|город|ст-ца|муниципальный округ|сдт|рп) (.+)$", re.UNICODE)
rx_div_end = re.compile(u"^(.+) (сельсовет|муниципальный район|муниципальный округ)$", re.UNICODE)


def normalize_division(s):
    """
    Normalize division and split short name
    :returns: (short name, name)
    """
    if isinstance(s, str):
        s = unicode(s)
    match = rx_div_start.match(s)
    if match:
        sn, n = match.groups()
        return div_norm.get(sn, sn), n
    match = rx_div_end.search(s)
    if match:
        n, sn = match.groups()
        return sn, n
    return None, s
