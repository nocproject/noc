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
