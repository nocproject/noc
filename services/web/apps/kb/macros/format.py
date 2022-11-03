# ---------------------------------------------------------------------
# format macro
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name

# NOC modules
from noc.core.profile.loader import loader as profile_loader
from .base import BaseMacro


class NOCHtmlFormatter(HtmlFormatter):
    """
    HTML Formatter
    Returns escaped HTML text with neat line numbers
    """

    name = "NOC HTML"

    def __init__(self, **kwargs):
        kwargs["linenos"] = "table"
        super().__init__(**kwargs)


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
