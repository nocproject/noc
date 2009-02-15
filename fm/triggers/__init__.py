# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Event triggers handlers
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.lib.registry import Registry
import re
##
## Event Trigger Registry
## Performs triggers search and initialization
## inside fm/triggers/ directory
##
class EventTriggerRegistry(Registry):
    name="EventTriggerRegistry"
    subdir="triggers"
    classname="EventTrigger"
    apps=["noc.fm"]
event_trigger_registry=EventTriggerRegistry()

##
## Metaclass for EventTrigger.
## Performs trigger registration in Event Trigger Registry
##
class EventTriggerBase(type):
    def __new__(cls,name,bases,attrs):
        m=type.__new__(cls,name,bases,attrs)
        event_trigger_registry.register(m.name,m)
        return m
##
## Event Trigger base class
##
class EventTrigger(object):
    __metaclass__=EventTriggerBase
    ## trigger name
    name=None
    ##
    ## Overload handle method to implement trigger functionality
    ## event is EventClass instance
    ##
    def handle(self,event):
        pass
