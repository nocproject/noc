# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Huawei.VRP highlight lexers
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from pygments.lexer import RegexLexer
from pygments.token import *
##
## Huawei VRP configuration lexer
##
class ConfigLexer(RegexLexer):
    name="Huawei.VRP"
    tokens={
        "root" : [
            (r"^!.*", Comment),
            (r"^(?:undo\s+)?\S+", Keyword),
            (r".*\n", Text),
        ]
    }
