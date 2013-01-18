# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alcatel.7302 highlight lexers
## Author: scanbox@gmail.com
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from pygments.lexer import RegexLexer,bygroups,include
from pygments.token import *


class ConfigLexer(RegexLexer):
    name = "Alcatel.7302"
    tokens = {
        "root": [
            (r"^#.*", Comment),
            (r"(description\s+)(\".*?\")", bygroups(Text, Comment)),
            (r"(user\s+)(\".*?\")", bygroups(Text, Comment)),
            (r"(user\s+)(.*?\s+)", bygroups(Text, Comment)),
            (r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(/\d+)?", Number),  # IPv4 Address/Prefix
            (r"(lt\:\d+\/\d+\/\d+)", Number),  # CardNumber
            (r"(\d+\/\d+\/\d+\/\d+)(\:\d+)*", Number),  # PortNumber
            (r"\s+\d+\s+\d*|,\d+", Number),
            (r".", Text),
        ],
    }
