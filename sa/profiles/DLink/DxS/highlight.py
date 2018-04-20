# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS highlight lexers
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from pygments.lexer import RegexLexer, bygroups, include
from pygments.token import *


class ConfigLexer(RegexLexer):
    name = "DLink.DxS"
    tokens = {
        "root": [
            (r"^!.*", Comment),
            (r"^#.*", Comment),
            (r"^\s*(enable)", Keyword),
            (r"(\s\w+)(?!\n)(\s+enabled*)", bygroups(Name.Class, Keyword)),
            (r"^\s*(config)", Name.Class),
            (r"^\s*(disable)", Generic.Deleted),
            (r"(\s\w+)(?!\n)(\s+disabled*)", bygroups(Name.Class, Generic.Deleted)),
            (r"^\s*(create)", Generic.Heading),
            (r"^\s*(debug|delete)", String.Other),
            (r"(description)(.*?)$", bygroups(Keyword, Comment)),
            (r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(/\d{1,2})?", Number),
            (r"(\s+[0-9A-F]{2}(\-|:)[0-9A-F]{2}(\-|:)[0-9A-F]{2}(\-|:)[0-9A-F]{2}(\-|:)[0-9A-F]{2}(\-|:)[0-9A-F]{2})", Name.Tag),
            (r"\s+\d+\s+\d*|\s+\d+,\d+|\s+\d+\-\d+|\s+\d+:\d+|\s+\d+:\(\d+|:\(\d+|,\d+\)*|-\d+\)*", Number),
            (r".", Text),
        ],
    }
