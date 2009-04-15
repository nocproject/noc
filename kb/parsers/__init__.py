# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Abstract Wiki parsers class
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.registry import Registry
from noc.lib.validators import is_int

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
    def to_html(cls,text):
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
    ##   KB<b> - Link to Knowledge Base article N
    ##
    @classmethod
    def convert_link(cls,link):
        if link.startswith("KB") and is_int(link[2:]):
            return u"<a href='/kb/%s/'>%s</a>"%(link[2:],link)
        else:
            return link

