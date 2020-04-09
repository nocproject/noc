# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Compatibility routines
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import six
from typing import List

DEFAULT_ENCODING = "utf-8"


def smart_bytes(s, encoding=DEFAULT_ENCODING):
    """
    Convert strings to bytes when necessary
    """
    if isinstance(s, six.binary_type):
        return s
    if isinstance(s, six.text_type):
        return s.encode(encoding)
    return six.text_type(s).encode(encoding)


def smart_text(s, errors="strict", encoding=DEFAULT_ENCODING):
    """
    Convert bytes to string when necessary
    """
    if isinstance(s, six.text_type):
        return s
    if isinstance(s, six.binary_type):
        return s.decode(encoding, errors=errors)
    return six.text_type(s)


def bord(x):
    # type: (int) -> int
    return x


def bchr(x):
    # type: (int) -> bytes
    return bytes([x])


def make_bytes(x):
    # type: (List[int]) -> bytes
    return bytes(x)
