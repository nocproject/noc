# ----------------------------------------------------------------------
# Utils for orjson
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


# NOC modules
from noc.core.ip import IP
from noc.core.mac import MAC


def orjson_defaults(obj):
    if isinstance(obj, (IP, MAC)):
        return str(obj)
    raise TypeError
