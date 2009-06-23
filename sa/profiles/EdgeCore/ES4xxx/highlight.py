# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## EdgeCore.ES4xxx highlight lexers
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from pygments.lexer import RegexLexer, bygroups
from pygments.token import *
##
## EdgeCore ES4xxx configuration lexer
##
class ConfigLexer(RegexLexer):
    name="EdgeCore.ES4xxx"
    tokens={
        "root" : [
            (r"(password\s+7\s+)(\S+)",bygroups(Keyword,String.Double)),
            (r"^(interface\s+\S+)(.*?)$", bygroups(Keyword,Name.Attribute)),
            (r"^(?:no\s+)?\S+", Keyword),
            (r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(/\d{1,2})?", Number), # IPv4 Address/Prefix
            (r"\d+", Number),
            (r".",   Text),
        ],
    }
