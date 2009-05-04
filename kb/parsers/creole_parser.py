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
## Macro wrapper
##
class MacroWrapper(object): pass
macro_wrapper=MacroWrapper()
for n,c in noc.kb.parsers.macro_registry.classes.items():
    setattr(macro_wrapper,n,c.expand)
##
## Creole Parser
##
class Parser(noc.kb.parsers.Parser):
    name="Creole"
    @classmethod
    def to_html(cls,kb_entry):
        def custom_link_emit(node):
            if node.children:
                text=html_emitter.emit_children(node)
            else:
                text=None
            return cls.convert_link(kb_entry,node.content,text)
        def custom_image_emit(node):
            target=cls.convert_attach(kb_entry,node.content)
            text=html_emitter.get_text(node)
            return u'<img src="%s" alt="%s" />' % (html_emitter.attr_escape(target),html_emitter.attr_escape(text))
        import creole
        parser=creole.Parser(unicode(kb_entry.body))
        html_emitter=creole.HtmlEmitter(parser.parse(),macros=macro_wrapper)
        html_emitter.link_emit=custom_link_emit
        html_emitter.image_emit=custom_image_emit
        return html_emitter.emit()
