# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DGS3100 highlight lexers
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from pygments.lexer import RegexLexer, bygroups, include
from pygments.token import *


class ConfigLexer(RegexLexer):
    name = "DLink.DGS3100"
    tokens = {
        "root": [
            (r"^!.*", Comment),
            (r"^#.*", Comment),
            (r"^(enable)", Keyword),
            (r"(\s\w+)(?!\n)(\s+enable)", bygroups(Name.Class, Keyword)),
            (r"^(config)", Name.Class),
            (r"^(disable)", Generic.Deleted),
            (r"(\s\w+)(?!\n)(\s+disable)", bygroups(Name.Class, Generic.Deleted)),
            (r"^(create)", Generic.Heading),
            (r"^(debug|delete)", String.Other),
            (r"(description)(.*?)$", bygroups(Keyword, Comment)),
            (r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(/\d{1,2})?", Number), # IPv4 Address/Prefix
            (r"(\s+[0-9A-F]{2}\-[0-9A-F]{2}\-[0-9A-F]{2}\-[0-9A-F]{2}\-[0-9A-F]{2}\-[0-9A-F]{2})", Name.Tag), # MAC Address
            (r"\s+\d+\s+\d*|\s+\d+,\d+|\s+\d+\-\d+|\s+\d+:\d+|\s+\d+:\(\d+|:\(\d+|,\d+\)*|-\d+\)*", Number),
            (r".", Text),
        ],
    }
