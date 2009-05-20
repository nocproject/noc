# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Force10.FTOS highlight lexers
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from pygments.lexer import RegexLexer, bygroups
from pygments.token import *
##
## Force10 FTOS configuration lexer
##
class ConfigLexer(RegexLexer):
    name="Force10.FTOS"
    tokens={
        "root" : [
            (r"^!.*", Comment),
            (r"(description)(.*?)$", bygroups(Keyword,Comment)),
            (r"(password|secret)(\s+[57]\s+)(\S+)", bygroups(Keyword,Number,String.Double)),
            (r"^(interface)(.*?)$", bygroups(Keyword,Name.Attribute)),
            (r"^(?:no\s+)?\S+", Keyword),
            (r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(/\d{1,2})?", Number), # IPv4 Address/Prefix
            (r"49\.\d{4}\.\d{4}\.\d{4}\.\d{4}\.\d{2}",           Number), # NSAP
            (r"\d+", Number),
            (r".", Text),
        ]
    }
