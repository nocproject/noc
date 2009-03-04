# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SLA Probe
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.lib.registry import Registry
##
## Probe registry
##
class ProbeRegistry(Registry):
    name="ProbeRegistry"
    subdir="probes"
    classname="Probe"
    apps=["noc.pm"]
probe_registry=ProbeRegistry()
##
## Metaclass for Probe
##
class ProbeBase(type):
    def __new__(cls,name,bases,attrs):
        m=type.__new__(cls,name,bases,attrs)
        m.scripts={}
        probe_registry.register(m.name,m)
        return m
##
## SLA Probe
##
class Probe(object):
    __metaclass__=ProbeBase
    name=None
    def __init__(self,probe_name,monitor,config):
        self.probe_name=probe_name
        self.monitor=monitor
        self.factory=monitor.factory
        self.result={}
        self.config=config
    ##
    ## Run method should call feed_result
    ##
    def run(self):
        pass
    ##
    ##
    ##
    def feed_result(self,object,result):
        self.result[object]=result
        print object,result
    ##
    ##
    ##
    def get(self,name,default=None):
        if self.config.has_option(self.probe_name,name):
            return self.config.get(self.probe_name,name)
        else:
            return default
