# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Creole 1.0 Parser (http://www.wikicreole.org)
## Requires python-creole
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
import noc.kb.parsers

##
## Creole Parser
##
class Parser(noc.kb.parsers.Parser):
    name="Creole"
    @classmethod
    def to_html(cls,text):
        import creole
        parser=creole.Parser(unicode(text))
        html_emitter=creole.HtmlEmitter(parser.parse())
        return html_emitter.emit()
