# ---------------------------------------------------------------------
# Plain text parser.
# Returns Raw Text
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from .base import BaseParser


class PlainTextParser(BaseParser):
    """Creole Parser"""

    name = "Plain Text"

    @classmethod
    def to_html(cls, kb_entry):
        return "<pre>%s</pre>" % kb_entry.body
