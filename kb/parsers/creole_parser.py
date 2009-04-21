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
    def to_html(cls,kb_entry):
        def custom_link_emit(node):
            link=creole.HtmlEmitter.link_emit(html_emitter,node)
            if link.startswith("<a href=\"http"):
                return link
            else:
                return cls.convert_link(kb_entry,link[link.index(">")+1:-4])
        def custom_image_emit(node):
            target=cls.convert_attach(kb_entry,node.content)
            text=html_emitter.get_text(node)
            return u'<img src="%s" alt="%s" />' % (html_emitter.attr_escape(target),html_emitter.attr_escape(text))
        import creole
        parser=creole.Parser(unicode(kb_entry.body))
        html_emitter=creole.HtmlEmitter(parser.parse())
        html_emitter.link_emit=custom_link_emit
        html_emitter.image_emit=custom_image_emit
        return html_emitter.emit()
