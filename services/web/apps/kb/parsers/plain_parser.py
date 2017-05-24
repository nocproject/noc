# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Plain text parser.
# Returns Raw Text
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
from noc.services.web.apps.kb.parsers import Parser


class Parser(Parser):
    """Creole Parser"""
    name = "Plain Text"

    @classmethod
    def to_html(cls, kb_entry):
        return u"<pre>%s</pre>" % kb_entry.body
