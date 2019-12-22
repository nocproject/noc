# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Creole 1.0 Parser (http://www.wikicreole.org)
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
from threading import Lock

# Third-party modules
import creole

# NOC modules
from ..macros.loader import loader as macro_loader
from .base import BaseParser
from noc.core.comp import smart_text

mw_lock = Lock()


class MacroWrapper(object):
    pass


class CreoleParser(BaseParser):
    name = "Creole"
    macro_wrapper = None

    @classmethod
    def to_html(cls, kb_entry):
        def custom_link_emit(node):
            if node.children:
                text = html_emitter.emit_children(node)
            else:
                text = None
            return cls.convert_link(kb_entry, node.content, text)

        def custom_image_emit(node):
            target = cls.convert_attach(kb_entry, node.content)
            text = html_emitter.get_text(node)
            return '<img src="%s" alt="%s" />' % (
                html_emitter.attr_escape(target),
                html_emitter.attr_escape(text),
            )

        parser = creole.Parser(smart_text(kb_entry.body))
        html_emitter = creole.HtmlEmitter(parser.parse(), macros=cls.get_macro_wrapper())
        html_emitter.link_emit = custom_link_emit
        html_emitter.image_emit = custom_image_emit
        return html_emitter.emit()

    @classmethod
    def get_macro_wrapper(cls):
        with mw_lock:
            if not cls.macro_wrapper:
                cls.macro_wrapper = MacroWrapper()
                for mn in macro_loader:
                    mc = macro_loader[mn]
                    setattr(cls.macro_wrapper, mn, mc.expand)
            return cls.macro_wrapper
