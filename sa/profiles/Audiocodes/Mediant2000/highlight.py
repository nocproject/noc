# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Audiocodes.Mediant2000 highlight lexers
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from pygments.lexer import RegexLexer
from pygments.token import *
##
## Audiocodes Mediant2000 configuration lexer
##
class ConfigLexer(RegexLexer):
    name="Audiocodes.Mediant2000"
    tokens={
        "root" : [
            (r"^;.*", Comment),
            (r"^\[.+\]", Keyword),
            (r"^.+(?==)", Name.Attribute),
            (r".*\n", Text),
        ]
    }
