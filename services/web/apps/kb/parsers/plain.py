# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Plain text parser.
# Returns Raw Text
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseParser


class PlainTextParser(BaseParser):
    """Creole Parser"""
    name = "Plain Text"

    @classmethod
    def to_html(cls, kb_entry):
        return u"<pre>%s</pre>" % kb_entry.body
