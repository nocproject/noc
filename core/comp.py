# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Compatibility routines
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from typing import List

DEFAULT_ENCODING = "utf-8"


def smart_bytes(s, encoding=DEFAULT_ENCODING):
    """
    Convert strings to bytes when necessary
    """
    if isinstance(s, bytes):
        return s
    if isinstance(s, str):
        return s.encode(encoding)
    return str(s).encode(encoding)


def smart_text(s, errors="strict", encoding=DEFAULT_ENCODING):
    """
    Convert bytes to string when necessary
    """
    if isinstance(s, str):
        return s
    if isinstance(s, bytes):
        return s.decode(encoding, errors=errors)
    return str(s)


def bord(x: int) -> int:
    return x


def bchr(x: int) -> bytes:
    return bytes([x])


def make_bytes(x: List[int]) -> bytes:
    return bytes(x)
