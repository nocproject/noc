# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alcatel.7302 highlight lexers
## made by scanbox@gmail.com
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from pygments.lexer import RegexLexer,bygroups,include
from pygments.token import *


class ConfigLexer(RegexLexer):
    name = "Alcatel.7302"
    tokens = {
        "root": [
            (r"^#.*", Comment),
            (r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", Number),  # IPv4 Address/Prefix
            (r".", Text),
        ],
    }
