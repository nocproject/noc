# ---------------------------------------------------------------------
# Abstract Wiki parsers class
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.validators import is_int

BASE_PATH = "/api/card/view/kb"


class BaseParser(object):
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

        :param kb_entry:
        :param link:
        :param text:
        :return:
        """
        if text is None:
            text = link
        if link.startswith("KB") and is_int(link[2:]):
            return "<a href='%s/%s/'>%s</a>" % (BASE_PATH, link[2:], text)
        if link.startswith("TT"):
            return link[2:]
        if link.startswith("attach:"):
            if text == link:
                text = link[7:]
            link = link[7:]
            return "<a href='%s/%d/attachment/%s/'>%s</a>" % (BASE_PATH, kb_entry.id, link, text)
        if link.startswith("attachment:"):
            if text == link:
                text = link[11:]
            link = link[11:]
            return "<a href='/kb/kbentry/%d/attachment/%s/'>%s</a>" % (kb_entry.id, link, text)
        try:
            le = kb_entry.__class__.objects.get(subject=link)
            return "<a href='%s/%s/'>%s</a>" % (BASE_PATH, le.id, text)
        except kb_entry.__class__.DoesNotExist:
            return "<a href='%s'>%s</a>" % (link, text)

    @classmethod
    def convert_attach(cls, kb_entry, href):
        """Convert attachment ref"""
        if href.startswith("http"):
            return href
        if href.startswith("attach:"):
            href = href[7:]
        elif href.startswith("attachment:"):
            href = href[11:]
        return "/kb/kbentry/%d/attachment/%s/" % (kb_entry.id, href)
