# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Juniper.ScreenOS highlight lexers
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from pygments.lexer import RegexLexer
from pygments.token import *
##
## Juniper ScreenOS configuration lexer
##
class ConfigLexer(RegexLexer):
    name="Juniper.ScreenOS"
    tokens={
        "root" : [
            (r"^!.*", Comment),
            (r"^(?:un)set\s+?\S+", Keyword),
            (r".*\n", Text),
        ]
    }
