# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Plain text parser.
## Returns Raw Text
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
import noc.kb.parsers

##
## Creole Parser
##
class Parser(noc.kb.parsers.Parser):
    name="Plain Text"
    @classmethod
    def to_html(cls,text):
        return u"<pre>%s</pre>"%text
