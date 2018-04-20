# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MediaWiki Parser (http://www.mediawiki.org)
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
## Python modules
import re
## NOC modules
import noc.kb.parsers
##
## MediaWiki parser
##
class Parser(noc.kb.parsers.Parser):
    name="MediaWiki"
    css=["mediawiki/shared.css", "mediawiki/main.css"]
    
    class NOCDB(object):
        rx_link=re.compile(r"<a href='(.+?)'>")
        def __init__(self, kb_entry):
            self.kb_entry=kb_entry
            
        def getURL(self, title, revision=None):
            url=Parser.convert_link(self.kb_entry, title)
            return self.rx_link.search(url).group(1)
        
        def get_siteinfo(self):
            from mwlib import siteinfo
            return siteinfo.get_siteinfo("en")
    
    @classmethod
    def to_html(cls,kb_entry):
        from mwlib.uparser import parseString
        from mwlib.xhtmlwriter import MWXHTMLWriter, preprocess
        try:
            import xml.etree.ElementTree as ET
        except:
            from elementtree import ElementTree as ET
        r=kb_entry.body.replace("\r", "")
        parsed=parseString(title=kb_entry.subject, raw=r, wikidb=cls.NOCDB(kb_entry))
        preprocess(parsed)
        xhtml=MWXHTMLWriter()
        xhtml.writeBook(parsed)
        block=ET.tostring(xhtml.xmlbody)
        return block
    
