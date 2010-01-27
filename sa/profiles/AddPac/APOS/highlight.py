# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AddPac.APOS highlight lexers
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from pygments.lexer import RegexLexer,bygroups,include
from pygments.token import *
##
## Cisco IOS configuration lexer
##
class ConfigLexer(RegexLexer):
    name="AddPac.APOS"
    tokens={
        "root" : [
            (r"^!.*", Comment),
            (r"(description)(.*?)$", bygroups(Keyword,Comment)),
            (r"(password|secret)(\s+[57]\s+)(\S+)", bygroups(Keyword,Number,String.Double)),
            (r"^(interface|controller|router \S+|voice translation-\S+|voice-port)(.*?)$", bygroups(Keyword,Name.Attribute)),
            (r"^(dial-peer\s+\S+\s+)(\S+)(.*?)$", bygroups(Keyword,Name.Attribute,Keyword)),
            (r"^(vlan\s+)(\d+)$", bygroups(Keyword,Name.Attribute)),
            (r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(/\d{1,2})?", Number), # IPv4 Address/Prefix
            (r"^(?:no\s+)?\S+", Keyword),
            (r"\d+", Number),
            (r".", Text),
        ],
        
    }
