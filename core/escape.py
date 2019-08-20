# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Escape/unescape to various encodings
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import binascii


def json_escape(s):
    """
    Escape JSON predefined sequences
    """
    if isinstance(s, bool):
        return "true" if s else "false"
    if s is None:
        return ""
    return s.replace("\\", "\\\\").replace("\n", "\\n").replace('"', '\\"')


def fm_escape(s):
    """
    Escape binary FM data to string
    """
    return binascii.b2a_qp(str(s)).replace("=\n", "")


def fm_unescape(s):
    """
    Decode escaped FM data to a raw string
    'ab\\xffcd'
    """
    return binascii.a2b_qp(str(s))
