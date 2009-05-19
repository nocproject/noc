# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.FWSM highlight lexers
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from pygments.lexer import RegexLexer
from pygments.token import *
##
## Cisco FWSM configuration lexer
##
class ConfigLexer(RegexLexer):
    name="Cisco.FWSM"
    tokens={
        "root" : [
            (r"^!.*", Comment),
            (r"^(?:no\s+)?\S+", Keyword),
            (r".*\n", Text),
        ]
    }
