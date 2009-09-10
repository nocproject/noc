# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.GbE2 highlight lexers
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from pygments.lexer import RegexLexer,bygroups,include
from pygments.token import *
##
## HP GbE2 configuration lexer
##
class ConfigLexer(RegexLexer):
    name="HP.GbE2"
    tokens={
        "root" : [
            (r"/\*", Comment),
            (r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(/\d{1,2})?", Number), # IPv4 Address/Prefix
            (r"^/\S*", Keyword),
            (r"\d+", Number),
            (r".", Text),
        ],
        
    }
