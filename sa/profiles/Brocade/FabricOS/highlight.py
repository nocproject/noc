# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Brocade.FabricOS highlight lexers
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from pygments.lexer import RegexLexer
from pygments.token import *


class ConfigLexer(RegexLexer):
    name = "Brocade.FabricOS"
    tokens = {
        "root": [
            #(r"^;.*", Comment),
            (r"^\[.+\]", Keyword),
            (r"^.+(?=:)", Name.Attribute),
            (r".*\n", Text)
        ]
    }
