# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Binary data to string encoder/decoder
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
import six

# Patterns

rx_unqoute = re.compile(r"\\x([0-9a-f][0-9a-f])", re.MULTILINE | re.DOTALL)
# Map to convert two-char hex to integer
hex_map = {"%02x" % i: chr(i) for i in range(256)}


def bin_quote(s):
    """
    Quote binary data to ASCII-string
    >>> bin_quote(None)
    ''
    >>> bin_quote("A")
    'A'
    """

    def qc(c):
        if c == "\\":
            return "\\\\"
        oc = ord(c)
        if oc < 32 or oc > 126:
            return "\\x%02x" % oc
        return c

    if s is None:
        return ""
    else:
        if isinstance(s, six.text_type):
            s = s.encode("utf-8")
        return "".join([qc(c) for c in s])


def bin_unquote(s):
    """
    Decode ASCII-encoded string back to binary

    >>> [i for i in range(256) if bin_unquote(bin_quote(chr(i)))!=chr(i)]
    []
    """
    if isinstance(s, six.text_type):
        s = s.encode("utf-8")
    return rx_unqoute.sub(lambda x: hex_map[x.group(1)], str(s).replace(r"\\", "\\x5c"))
