# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Compatibility routines
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

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


def reraise(tp, value, tb=None):
    try:
        if value is None:
            value = tp()
        if value.__traceback__ is not tb:
            raise value.with_traceback(tb)
        raise value
    finally:
        value = None
        tb = None
