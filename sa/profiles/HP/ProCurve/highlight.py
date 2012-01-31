# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.ProCurve highlight lexers
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from pygments.lexer import RegexLexer, bygroups
from pygments.token import *


class ConfigLexer(RegexLexer):
    name = "HP.ProCurve"
    tokens = {
        "root": [
            (r"^#.*", Comment),
            (r"^(banner motd) (\"[^\"]+\")", bygroups(Keyword, Comment)),
            (r"(name)(.*?)$", bygroups(Keyword, Comment)),
            (r"^(interface)(.*?)$", bygroups(Keyword, Name.Attribute)),
            (r"^(vlan\s+)(\d+)$", bygroups(Keyword, Name.Attribute)),
            (r"^(?:no\s+)?\S+", Keyword),
            (r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(/\d{1,2})?", Number),  # IPv4 Address/Prefix
            (r"\d+", Number),
            (r".", Text)
        ]
    }
