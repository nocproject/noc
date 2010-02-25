# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Abstract Wiki parsers class
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.registry import Registry
from noc.lib.validators import is_int
from noc.settings import config
from noc.kb.parsers.macros import macro_registry

macro_registry.register_all()

##
## Parser Registry
##
class ParserRegistry(Registry):
    name="ParserRegistry"
    subdir="parsers"
    classname="Parser"
    apps=["noc.kb"]
parser_registry=ParserRegistry()

##
## Metaclass for Parser
##
class ParserBase(type):
    def __new__(cls,name,bases,attrs):
        m=type.__new__(cls,name,bases,attrs)
        parser_registry.register(m.name,m)
        return m
##
## Abstract parser class
##
class Parser(object):
    __metaclass__=ParserBase
    name=None
    ##
    ## Convert wiki syntax to HTML
    ##
    @classmethod
    def to_html(cls,kb_entry):
        raise "Does not implemented"
    ##
    ## Check syntax
    ##
    @classmethod
    def check(cls,text):
        cls.to_html(text)
    ##
    ## Convert extracted link to URL
    ## Following link types are supported:
    ##   KB<n> - Link to Knowledge Base article <n>
    ##   TT<n> - Link to Trouble Ticket <n>
    ##   attach:<name> - Link to attachment <name>
    @classmethod
    def convert_link(cls,kb_entry,link,text=None):
        if text is None:
            text=link
        if link.startswith("KB") and is_int(link[2:]):
            return u"<a href='/kb/%s/'>%s</a>"%(link[2:],text)
        elif link.startswith("TT"):
            tt={"tt":link[2:]}
            tt_url=config.get("tt","url",tt)%tt
            return u"<a href='%s'>%s</a>"%(tt_url,text)
        elif link.startswith("attach:"):
            if text==link:
                text=link[7:]
            link=link[7:]
            return u"<a href='/kb/%d/attachment/%s/'>%s</a>"%(kb_entry.id,link,text)
        elif link.startswith("attachment:"):
            if text==link:
                text=link[11:]
            link=link[11:]
            return u"<a href='/kb/%d/attachment/%s/'>%s</a>"%(kb_entry.id,link,text)
        else:
            return u"<a href='%s'>%s</a>"%(link,text)
    ##
    ## Convert attachment ref
    ##
    @classmethod
    def convert_attach(cls,kb_entry,href):
        if href.startswith("http"):
            return href
        elif href.startswith("attach:"):
            name=href[7:]
        elif href.startswith("attachment:"):
            href=href[11:]
        return "/kb/%d/attachment/%s/"%(kb_entry.id,href)

