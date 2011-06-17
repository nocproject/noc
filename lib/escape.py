# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Escape/unescape to various encodings
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import binascii


##
## JSON
##
def json_escape(s):
    """
    Escape JSON predefined sequences
    """
    if type(s) == bool:
        return "true" if s else "false"
    return s.replace("\\", "\\\\").replace("\n", "\\n").replace("\"", "\\\"")


##
## Fault management
##
def fm_escape(s):
    """
    Escape binary FM data to string
    
    >>> fm_escape("ab\xffcd")
    'ab=FFcd'
    """
    return binascii.b2a_qp(str(s)).replace("=\n", "")


def fm_unescape(s):
    """
    Decode escaped FM data to a raw string
    
    >>> fm_unescape("ab=FFcd")
    'ab\\xffcd'
    """
    return binascii.a2b_qp(str(s))
