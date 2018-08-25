# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# format macro
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# Third-party modules
from pygments import highlight
from pygments.lexers import get_lexer_by_name
# NOC modules
from noc.lib.highlight import NOCHtmlFormatter
from noc.core.profile.loader import loader as profile_loader
from .base import BaseMacro


class FormatMacro(BaseMacro):
    """
    Format macro:
    Formats and highlights text
    Args:
        syntax - name of the syntax.
    """
    name = "format"

    @classmethod
    def handle(cls, args, text):
        if "syntax" in args:
            format = args["syntax"]
        else:
            format = "text"
        if format.startswith("noc."):
            profile_name = format[4:]
            try:
                profile = profile_loader.get_profile(profile_name)
            except Exception:
                profile = None
                format = "text"
            if profile:
                return profile().highlight_config(text)
        try:
            lexer = get_lexer_by_name(format)
        except Exception:
            lexer = get_lexer_by_name("text")
        return highlight(text, lexer, NOCHtmlFormatter())
