# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Extreme.XOS highlight lexers
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from pygments.lexer import RegexLexer, bygroups
from pygments.token import *


class ConfigLexer(RegexLexer):
    name = "Extreme.XOS"
    tokens = {
        "root": [
            (r"\"", String.Double, "string"),
            (r"(Module)(.*?)$", bygroups(Keyword, Comment)),
            (r"^(port\s+\S+|svlan\s+\S+\s+\S+)(.*?)$", bygroups(Keyword, Name.Attribute)),
            (r"^(?:set\s+)?\S+", Keyword),
            (r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(/\d{1,2})?", Number),  # IPv4 Address/Prefix
            (r"\d+", Number),
            (r".", Text),
        ],
        "string": [
            (r".*\"", String.Double, "#pop")
        ]
    }
