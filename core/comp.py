# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Compatibility routines
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import six
from typing import List

DEFAULT_ENCODING = "utf-8"


def smart_bytes(s):
    """
    Convert strings to bytes when necessary
    """
    if isinstance(s, six.binary_type):
        return s
    if isinstance(s, six.text_type):
        return s.encode(DEFAULT_ENCODING)
    return six.text_type(s).encode(DEFAULT_ENCODING)


def smart_text(s, errors="strict"):
    """
    Convert bytes to string when necessary
    """
    if isinstance(s, six.text_type):
        return s
    if isinstance(s, six.binary_type):
        return s.decode(DEFAULT_ENCODING, errors=errors)
    return six.text_type(s)


if six.PY3:

    def bord(x):
        # type: (int) -> int
        return x

    def bchr(x):
        # type: (int) -> bytes
        return bytes([x])

    def make_bytes(x):
        # type: (List[int]) -> bytes
        return bytes(x)


else:

    def bord(x):
        # type: (bytes) -> int
        return ord(x)

    def bchr(x):
        # type: (bytes) -> bytes
        return x

    def make_bytes(x):
        # type: (List[bytes]) -> bytes
        return b"".join(x)
