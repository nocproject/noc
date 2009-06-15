# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Reduce Scripts
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.registry import Registry
class ReduceScriptRegistry(Registry):
    name="ReduceScriptRegisry"
    subdir="scripts"
    classname="ReduceScript"
    apps=["noc.sa"]
reduce_script_registry=ReduceScriptRegistry()
##
## Metaclass for ReduceScript
##
class ReduceScriptBase(type):
    def __new__(cls,name,bases,attrs):
        m=type.__new__(cls,name,bases,attrs)
        m.scripts={}
        reduce_script_registry.register(m.name,m)
        return m
##
## Basic reduce script
##
class ReduceScript(object):
    __metaclass__=ReduceScriptBase
    name=None
    ##
    ## Execute reduce script
    ## Accepts ReduceTask at input
    ## Returns formatted HTML with result
    ## Kwargs are passed from reduce task params
    ##
    @classmethod
    def execute(cls,task,**kwargs):
        return ""
