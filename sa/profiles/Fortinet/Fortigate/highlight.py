# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Fortinet.Fortigate highlight lexers
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from pygments.lexer import RegexLexer,bygroups
from pygments.token import *

class ConfigLexer(RegexLexer):
    """
    Fortinet Fortigate configuration lexer
    """
    name = "Fortinet.Fortigate"
    tokens = {
        "root": [
            (r"^#.*", Comment),
            (r"(password|psksecret)(\sENC)(\S+)", bygroups(Keyword,
                                                           String.Double)),
            (r"^(interface)(.*?)$", bygroups(Keyword,
                                             Name.Attribute)),
            (r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(/\d{1,2})?", Number),
            (r"\d+", Number),
            (r".", Text),
        ]
    }
