# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Application menu builder
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.settings
import types
##
## Registered menu list
##
MENU=[]
##
## Menu metaclass
## Performs menu registration
##
class MenuBase(type):
    def __new__(cls,name,bases,attrs):
        def convert(x):
            if type(x[1])==types.ListType:
                return (x[0],{"items":x[1]})
            else:
                return x
        m=type.__new__(cls,name,bases,attrs)
        if m.app and m.title:
            r={
                "app"   : m.app,
                "title" : m.title,
                "items" : [convert(x) for x in m.items],
            }
            MENU.append(r)
        return m
##
## Application menu class.
##
class Menu(object):
    __metaclass__=MenuBase
    app=None     # Application name
    title=None # Application title
    items=[]   # list of (title,link)
