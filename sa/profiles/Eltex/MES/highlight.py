# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Eltex.MES highlight lexers
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from pygments.lexer import RegexLexer, bygroups, include
from pygments.token import *


class ConfigLexer(RegexLexer):
    name = "Eltex.MES"

    tokens = {"root": [
            (r"^!.*", Comment),
            (r"(description)(.*?)$", bygroups(Keyword, Comment)),
            (r"(password|shared-secret|secret)(\s+[57]\s+)(\S+)",
                bygroups(Keyword, Number, String.Double)),
            (r"(ca trustpoint\s+)(\S+)", bygroups(Keyword, String.Double)),
            (r"^(interface|controller|router \S+|voice translation-\S+|voice-port)(.*?)$",
                bygroups(Keyword, Name.Attribute)),
            (r"^(dial-peer\s+\S+\s+)(\S+)(.*?)$",
                bygroups(Keyword, Name.Attribute, Keyword)),
            (r"^(vlan\s+)(\d+)$", bygroups(Keyword, Name.Attribute)),
            # IPv4 Address/Prefix
            (r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(/\d{1,2})?", Number),
            # NSAP
            (r"49\.\d{4}\.\d{4}\.\d{4}\.\d{4}\.\d{2}", Number),
            # MAC Address
            (r"(\s+[0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4}\s+)", Number),
            (r"^(?:no\s+)?\S+", Keyword),
            (r"\s+\d+\s+\d*|,\d+|-\d+", Number),
            (r".", Text),
        ]}
