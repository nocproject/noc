# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Linksys.VoIP highlight lexers
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from pygments.lexer import RegexLexer
from pygments.token import *


class ConfigLexer(RegexLexer):
    name = "Linksys.VoIP"
    tokens = {
        "root": [
            (r"^;.*", Comment),
            (r"^\[.+\]", Keyword),
            (r"^.+(?==)", Name.Attribute),
            (r".*\n", Text),
        ]
    }
