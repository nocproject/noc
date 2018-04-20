# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AlliedTelesis.AT8000S highlight lexers
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from pygments.lexer import RegexLexer,bygroups,include
from pygments.token import *


class ConfigLexer(RegexLexer):
    name = "AlliedTelesis.AT8000S"
    tokens = {
        "root": [
            (r"^!.*", Comment),
            (r"(description)(.*?)$", bygroups(Keyword, Comment)),
            (r"(password|secret)(\s+[57]\s+)(\S+)", bygroups(Keyword, Number, String.Double)),
            (r"^(interface|controller|router \S+|voice translation-\S+|voice-port)(.*?)$", bygroups(Keyword, Name.Attribute)),
            (r"^(dial-peer\s+\S+\s+)(\S+)(.*?)$", bygroups(Keyword, Name.Attribute, Keyword)),
            (r"^(vlan\s+)(\d+)$", bygroups(Keyword, Name.Attribute)),
            (r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(/\d{1,2})?", Number),  # IPv4 Address/Prefix
            (r"49\.\d{4}\.\d{4}\.\d{4}\.\d{4}\.\d{2}", Number),  # NSAP
            (r"^(?:no\s+)?\S+", Keyword),
            (r"\d+", Number),
            (r".", Text)
        ]
    }
