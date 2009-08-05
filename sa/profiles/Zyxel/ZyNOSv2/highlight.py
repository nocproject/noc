# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ZyXEL.ZyNOSv2 highlight lexers
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from pygments.lexer import RegexLexer, bygroups
from pygments.token import *
##
## ZyXEL ZyNOS configuration lexer
##
class ConfigLexer(RegexLexer):
    name="Zyxel.ZyNOSv2"
    tokens={
        "root" : [
            (r"\"",             String.Double, "string"),
            (r"(Module)(.*?)$",   bygroups(Keyword,Comment)),
            (r"^(port\s+\S+|svlan\s+\S+\s+\S+)(.*?)$", bygroups(Keyword,Name.Attribute)),
            (r"^(?:set\s+)?\S+", Keyword),
            (r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(/\d{1,2})?", Number), # IPv4 Address/Prefix
            (r"\d+", Number),
            (r".",   Text),
        ],
        "string" : [
            (r".*\"", String.Double, "#pop"),
        ]
    }
