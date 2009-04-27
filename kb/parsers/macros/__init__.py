# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Macros Framework
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.registry import Registry
import types,re
##
## Macro Registry
##
class MacroRegistry(Registry):
    name="MacroRegistry"
    subdir="parsers/macros"
    classname="Macro"
    apps=["noc.kb"]
macro_registry=MacroRegistry()

##
## Metaclass for Macroses
##
class MacroBase(type):
    def __new__(cls,name,bases,attrs):
        m=type.__new__(cls,name,bases,attrs)
        macro_registry.register(m.name,m)
        return m
##
## Args regular expression
##
rx_args=re.compile(r"\s*(?P<attr>\S+)\s*=\s*(?P<quote>['\"])(?P<value>.*?)(?P=quote)")
##
## Macro Base
##
class Macro(object):
    __metaclass__=MacroBase
    name=None
    ##
    ## Converts a string of html-like attributes to hash
    ##
    @classmethod
    def parse_args(cls,args):
        if type(args)==types.DictType:
            return args
        return dict([(m[0],m[2]) for m in rx_args.findall(args)])
    ##
    ## Decodes args and calls handle method
    ##
    @classmethod
    def expand(cls,args,text):
        return cls.handle(cls.parse_args(args),text)
    ##
    ## Specific macro handler to be overriden in child classes
    ## Accepts a hash of args and text and returns formatted HTML
    ## to be included in output
    ##
    @classmethod
    def handle(cls,args,text):
        raise NotImplementedError

