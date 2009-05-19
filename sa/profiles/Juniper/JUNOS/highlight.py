# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Juniper.JUNOS highlight lexers
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from pygments.lexer import RegexLexer,bygroups
from pygments.token import *
##
## Juniper JUNOS configuration lexer
##
class ConfigLexer(RegexLexer):
    name="Juniper.JUNOS"
    tokens={
        "root" : [
            (r"#.*$",  Comment),
            (r"//.*$", Comment),
            (r"/\*",   Comment, "comment"),
            (r"\"",    String.Double, "string"),
            (r"(\S+\s+)(\S+\s+)({\s*)$", bygroups(Keyword,Name.Attribute,Punctuation) ),
            (r"(\S\s+)({\s*)$",          bygroups(Keyword,Punctuation)),
            (r"https?://.*?[;]", String.Double),
            (r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(/\d{1,2})?", Number), # IPv4 Address/Prefix
            (r"49\.\d{4}\.\d{4}\.\d{4}\.\d{4}\.\d{2}",           Number), # NSAP
            (r"[;\[\]/:<>*{}]",  Punctuation),
            (r'\s+',             Text),
            (r'\w[\w\.-]*[\w]+', Text),
            (r'\d+',             Number),
        ],
        "comment" : [
            (r"[^/*]", Comment),
            (r"/\*",   Comment, "#push"),
            (r"\*/",   Comment, "#pop"),
            (r"[*/]",  Comment),
        ],
        "string" : [
            (r".*\"", String.Double, "#pop"),
        ]
    }
