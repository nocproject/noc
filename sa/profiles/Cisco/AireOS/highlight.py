# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.AireOS highlight lexers
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
    name="Cisco.AireOS"
    tokens={
        "root" : [
            (r"^!.*", Comment),
            (r"(description)(.*?)$", bygroups(Keyword,Comment)),
            (r"(password|secret)(\s+[57]\s+)(\S+)", bygroups(Keyword,Number,String.Double)),
            (r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(/\d{1,2})?", Number), # IPv4 Address/Prefix
            (r"\d+", Number),
            (r".", Text),
        ],
        
    }
