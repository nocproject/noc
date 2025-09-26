# ---------------------------------------------------------------------
# MediaWiki Parser (http://www.mediawiki.org)
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

try:
    import xml.etree.ElementTree as ET
except Exception:
    from elementtree import ElementTree as ET
# Third-party modules
from mwlib import siteinfo
from mwlib.uparser import parseString
from mwlib.xhtmlwriter import MWXHTMLWriter, preprocess

# NOC modules
from .base import BaseParser


class MediaWikiParser(BaseParser):
    name = "MediaWiki"
    css = ["mediawiki/shared.css", "mediawiki/main.css"]

    class NOCDB(object):
        rx_link = re.compile(r"<a href='(.+?)'>")

        def __init__(self, kb_entry):
            self.kb_entry = kb_entry

        def getURL(self, title, revision=None):
            url = BaseParser.convert_link(self.kb_entry, title)
            return self.rx_link.search(url).group(1)

        def get_siteinfo(self):
            return siteinfo.get_siteinfo("en")

    @classmethod
    def to_html(cls, kb_entry):
        r = kb_entry.body.replace("\r", "")
        parsed = parseString(title=kb_entry.subject, raw=r, wikidb=cls.NOCDB(kb_entry))
        preprocess(parsed)
        xhtml = MWXHTMLWriter()
        xhtml.writeBook(parsed)
        return ET.tostring(xhtml.xmlbody)

    @classmethod
    def is_enabled(cls):
        return True
