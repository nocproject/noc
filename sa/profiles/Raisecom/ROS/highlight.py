# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Raisecom.ROS highlight lexers
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
    name="Raisecom.ROS"
    tokens={
        "root" : [
            (r"^!.*", Comment),
            (r"(description)(.*?)$", bygroups(Keyword,Comment)),
            (r"^(interface|vlan)(.*?)$", bygroups(Keyword,Name.Attribute)),
            (r"\d+", Number),
            (r".", Text),
        ],
        
    }
