# ----------------------------------------------------------------------
# Utils for orjson
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Any

# Third-party modules
import orjson

# NOC modules
from noc.core.ip import IP
from noc.core.mac import MAC


def orjson_defaults(obj):
    if isinstance(obj, (IP, MAC)):
        return str(obj)
    raise TypeError


def iter_chunks(data: Any, max_size: int) -> bytes:
    """
    Split Python data list to json chunk by max_size
    """
    if not isinstance(data, list):
        yield orjson.dumps(data)
        return
    r: bytes = b""
    size = 0
    for d in data:
        d = orjson.dumps(d)
        ld = len(d)
        if size + ld + 1 > max_size and r:
            yield b"[" + r + b"]"
            r = b""
            size = 0
        if r:
            r += b","
        r += d
        size += ld + (1 if size else 0)
    if r:
        yield b"[" + r + b"]"
