# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## format macro
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from pygments import highlight
from pygments.lexers import get_lexer_by_name

from noc.services.web.apps.kb.parsers.macros import Macro as MacroBase
from noc.lib.highlight import NOCHtmlFormatter
from noc.core.profile.loader import loader as profile_loader


##
## Format macro:
## Formats and highlights text
## Args:
##     syntax - name of the syntax.
##
class Macro(MacroBase):
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
            except:
                profile = None
                format = "text"
            if profile:
                return profile().highlight_config(text)
        try:
            lexer = get_lexer_by_name(format)
        except:
            lexer = get_lexer_by_name("text")
        return highlight(text, lexer, NOCHtmlFormatter())

