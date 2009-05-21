# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ZyXEL.ZyNOS highlight lexers
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
    name="Zyxel.ZyNOS"
    tokens={
        "root" : [
            (r"\"",             String.Double, "string"),
            (r"(name)(.*?)$",   bygroups(Keyword,Comment)),
            (r"^(interface\s+\S+|vlan\s+)(.*?)$", bygroups(Keyword,Name.Attribute)),
            (r"^(?:no\s+)?\S+", Keyword),
            (r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(/\d{1,2})?", Number), # IPv4 Address/Prefix
            (r"\d+", Number),
            (r".",   Text),
        ],
        "string" : [
            (r".*\"", String.Double, "#pop"),
        ]
    }
