# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS highlight lexers
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from pygments.lexer import RegexLexer
from pygments.token import *
##
## Cisco IOS configuration lexer
##
class ConfigLexer(RegexLexer):
    name="Cisco.IOS"
    tokens={
        "root" : [
            (r"^!.*", Comment),
            (r"^(?:no\s+)?\S+", Keyword),
            (r".*\n", Text),
        ]
    }
