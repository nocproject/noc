# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## H3C.VRP highlight lexers
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from pygments.lexer import RegexLexer, bygroups
from pygments.token import *


class ConfigLexer(RegexLexer):
    name = "H3C.VRP"
    tokens = {
        "root": [
            (r"^#.*", Comment),
            (r"(description)(.*?)$", bygroups(Keyword, Comment)),
            (r"^(interface|ospf|bgp|isis|acl name)(.*?)$", bygroups(Keyword, Name.Attribute)),
            (r"^(vlan\s+)(\d+)$", bygroups(Keyword, Name.Attribute)),
            (r"^(vlan\s+)(\d+\s+)(to\s+)(\d+)$", bygroups(Keyword, Name.Attribute, Keyword, Name.Attribute)),
            (r"^(?:undo\s+)?\S+", Keyword),
            (r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(/\d{1,2})?", Number),  # IPv4 Address/Prefix
            (r"49\.\d{4}\.\d{4}\.\d{4}\.\d{4}\.\d{2}", Number),  # NSAP
            (r"\d+", Number),
            (r".", Text),
        ]
    }
