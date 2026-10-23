# ---------------------------------------------------------------------
# Abstract Wiki parsers class
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules

# Third-party modules
from gufo.loader import Loader

# NOC modules
from noc.config import config
from noc.core.validators import is_int


BASE_PATH = "/api/card/view/kb"


class BaseParser:
    """
    Abstract parser class
    """

    name = None
    # A list of additional CSSs
    css = []

    @classmethod
    def is_enabled(cls):
        return True

    @classmethod
    def to_html(cls, kb_entry):
        """Convert wiki syntax to HTML"""
        raise NotImplementedError()

    @classmethod
    def check(cls, text):
        """Check syntax"""
        cls.to_html(text)

    @classmethod
    def convert_link(cls, kb_entry, link, text=None):
        """
        Convert extracted link to URL
        Following link types are supported:
        KB<n> - Link to Knowledge Base article <n>
        TT<n> - Link to Trouble Ticket <n>
        attach:<name> - Link to attachment <name>

        :return:
        """
        if text is None:
            text = link
        if link.startswith("KB") and is_int(link[2:]):
            return f"<a href='{BASE_PATH}/{link[2:]}/'>{text}</a>"
        if link.startswith("TT"):
            return link[2:]
        if link.startswith("attach:"):
            if text == link:
                text = link[7:]
            link = link[7:]
            return f"<a href='{BASE_PATH}/{int(kb_entry.id)}/attachment/{link}/'>{text}</a>"
        if link.startswith("attachment:"):
            if text == link:
                text = link[11:]
            link = link[11:]
            return f"<a href='/kb/kbentry/{int(kb_entry.id)}/attachment/{link}/'>{text}</a>"
        try:
            le = kb_entry.__class__.objects.get(subject=link)
            return f"<a href='{BASE_PATH}/{le.id}/'>{text}</a>"
        except kb_entry.__class__.DoesNotExist:
            return f"<a href='{link}'>{text}</a>"

    @classmethod
    def convert_attach(cls, kb_entry, href):
        """Convert attachment ref"""
        if href.startswith("http"):
            return href
        if href.startswith("attach:"):
            href = href[7:]
        elif href.startswith("attachment:"):
            href = href[11:]
        return f"/kb/kbentry/{int(kb_entry.id)}/attachment/{href}/"


kb_parser_loader = Loader[type[BaseParser]](
    bases=config.iter_customized_bases("noc.services.web.apps.kb.parsers"),
    exclude=("base",),
)
