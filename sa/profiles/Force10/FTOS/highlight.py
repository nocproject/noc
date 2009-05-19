# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Force10.FTOS highlight lexers
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from pygments.lexer import RegexLexer
from pygments.token import *
##
## Force10 FTOS configuration lexer
##
class ConfigLexer(RegexLexer):
    name="Force10.FTOS"
    tokens={
        "root" : [
            (r"^!.*", Comment),
            (r"^(?:no\s+)?\S+", Keyword),
            (r".*\n", Text),
        ]
    }
