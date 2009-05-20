# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.FWSM highlight lexers
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from pygments.lexer import RegexLexer,bygroups
from pygments.token import *
##
## Cisco FWSM configuration lexer
##
class ConfigLexer(RegexLexer):
    name="Cisco.FWSM"
    tokens={
        "root" : [
            (r"^!.*", Comment),
            (r"(password)(\s+\S+\s+)(encrypted)", bygroups(Keyword,String.Double,Keyword)),
            (r"^(interface|router\s+\S+)(.*?)$", bygroups(Keyword,Name.Attribute)),
            (r"^(group-policy)(\s+\S+\s+)(\S+)", bygroups(Keyword,Name.Attribute,Keyword)),
            (r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(/\d{1,2})?", Number), # IPv4 Address/Prefix
            (r"^(?:no\s+)?\S+", Keyword),
            (r"\d+", Number),
            (r".", Text),
        ]
    }
