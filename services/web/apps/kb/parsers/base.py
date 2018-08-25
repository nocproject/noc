# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Abstract Wiki parsers class
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from __future__ import absolute_import
from noc.lib.validators import is_int
from noc.settings import config


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
    #
    # Convert extracted link to URL
    # Following link types are supported:
    #   KB<n> - Link to Knowledge Base article <n>
    #   TT<n> - Link to Trouble Ticket <n>
    #   attach:<name> - Link to attachment <name>

    @classmethod
    def convert_link(cls, kb_entry, link, text=None):
        if text is None:
            text = link
        if link.startswith("KB") and is_int(link[2:]):
            return u"<a href='/kb/view/%s/'>%s</a>" % (link[2:], text)
        elif link.startswith("TT"):
            tt = {"tt": link[2:]}
            tt_url = config.get("tt", "url", tt) % tt
            return u"<a href='%s'>%s</a>" % (tt_url, text)
        elif link.startswith("attach:"):
            if text == link:
                text = link[7:]
            link = link[7:]
            return u"<a href='/kb/view/%d/attachment/%s/'>%s</a>" % (
                kb_entry.id, link, text
            )
        elif link.startswith("attachment:"):
            if text == link:
                text = link[11:]
            link = link[11:]
            return u"<a href='/kb/%d/attachment/%s/'>%s</a>" % (
                kb_entry.id, link, text
            )
        else:
            try:
                le = kb_entry.__class__.objects.get(subject=link)
                return u"<a href='/kb/view/%s/'>%s</a>" % (le.id, text)
            except kb_entry.__class__.DoesNotExist:
                return u"<a href='%s'>%s</a>" % (link, text)

    @classmethod
    def convert_attach(cls, kb_entry, href):
        """Convert attachment ref"""
        if href.startswith("http"):
            return href
        elif href.startswith("attach:"):
            href = href[7:]
        elif href.startswith("attachment:"):
            href = href[11:]
        return "/kb/view/%d/attachment/%s/" % (kb_entry.id, href)
