# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MediaWiki Parser (http://www.mediawiki.org)
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
import noc.kb.parsers

class Parser(noc.kb.parsers.Parser):
    name="MediaWiki"
    css=["mediawiki/shared.css", "mediawiki/main.css"]
    @classmethod
    def to_html(cls,kb_entry):
        from mwlib.dummydb import DummyDB
        from mwlib.uparser import parseString
        from mwlib.xhtmlwriter import MWXHTMLWriter, preprocess
        try:
            import xml.etree.ElementTree as ET
        except:
            from elementtree import ElementTree as ET
        db=DummyDB()
        r=kb_entry.body.replace("\r", "")
        parsed=parseString(title=kb_entry.subject, raw=r, wikidb=db)
        preprocess(parsed)
        xhtml=MWXHTMLWriter()
        xhtml.writeBook(parsed)
        block=ET.tostring(xhtml.xmlbody)
        return block
    
