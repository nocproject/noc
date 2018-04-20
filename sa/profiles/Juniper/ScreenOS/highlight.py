# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Juniper.ScreenOS highlight lexers
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from pygments.lexer import RegexLexer, bygroups
from pygments.token import *
##
## Juniper ScreenOS configuration lexer
##
class ConfigLexer(RegexLexer):
    name="Juniper.ScreenOS"
    tokens={
        "root" : [
            (r"\"",    String.Double, "string"),
            (r"^(?:un)?set\s+?\S+", Keyword),
            (r"^exit$", Keyword),
            (r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(/\d{1,2})?", Number), # IPv4 Address/Prefix
            (r"\d+", Number),
            (r".", Text),
        ],
        "string" : [
                (r".*\"", String.Double, "#pop"),
            ]
    }
