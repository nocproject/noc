# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Macros Framework
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.registry import Registry

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
## Macro Base
##
class Macro(object):
    __metaclass__=MacroBase
    name=None
    @classmethod
    def expand(cls,args,text):
        return u"Not implemented macro"
