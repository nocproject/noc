# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## f5.BIGIP highlight lexers
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from pygments.lexer import RegexLexer, bygroups
from pygments.token import *
##
## f5 BIGIP configuration lexer
##
class ConfigLexer(RegexLexer):
    name="f5.BIGIP"
    tokens={
        "root" : [
            (r"\"",    String.Double, "string"),
            (r"^(\S+\s+)(\S+\s+)({)$", bygroups(Keyword,Name.Attribute,Punctuation)),
            #(r"(description)(.*?)$", bygroups(Keyword,Comment)),
            #(r"(password|secret)(\s+[57]\s+)(\S+)", bygroups(Keyword,Number,String.Double)),
            #(r"^(interface)(.*?)$", bygroups(Keyword,Name.Attribute)),
            #(r"^(?:no\s+)?\S+", Keyword),
            (r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(/\d{1,2})?", Number), # IPv4 Address/Prefix
            (r"49\.\d{4}\.\d{4}\.\d{4}\.\d{4}\.\d{2}",           Number), # NSAP
            (r"[}]", Punctuation),
            (r"\d+", Number),
            (r".", Text),
        ],
        "string" : [
            (r".*\"", String.Double, "#pop"),
        ]
    }
