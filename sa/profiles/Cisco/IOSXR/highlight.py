# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOSXR highlight lexers
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from pygments.lexer import RegexLexer, bygroups, include
from pygments.token import *


class ConfigLexer(RegexLexer):
    name = "Cisco.IOSXR"
    tokens = {
        "root": [
            (r"^!.*", Comment),
            (r"(description)(.*?)$", bygroups(Keyword, Comment)),
            (r"(password|shared-secret|secret)(\s+[57]\s+)(\S+)", bygroups(Keyword, Number, String.Double)),
            (r"(ca trustpoint\s+)(\S+)", bygroups(Keyword, String.Double)),
            (r"^(interface|controller|router \S+)(.*?)$", bygroups(Keyword, Name.Attribute)),
            (r"^(vlan\s+)(\d+)$", bygroups(Keyword, Name.Attribute)),
            (r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(/\d{1,2})?", Number),  # IPv4 Address/Prefix
            (r"49\.\d{4}\.\d{4}\.\d{4}\.\d{4}\.\d{2}", Number),  # NSAP
            (r"(\s+[0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4}\s+)", Number),  # MAC Address
            (r"^(?:no\s+)?\S+", Keyword),
            (r"\s+\d+\s+\d*|,\d+|-\d+", Number),
            (r".", Text),
        ]
    }
