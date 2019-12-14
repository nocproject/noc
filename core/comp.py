# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Compatibility routines
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import six

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
