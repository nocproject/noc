# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import datetime,os
from noc.lib.registry import Registry

##
## Registry for all periodic tasks
##
class PeriodicRegistry(Registry):
    name="PeriodicRegistry"
    subdir="periodics"
    classname="Task"
    
periodic_registry=PeriodicRegistry()

##
## Metaclass for Task
##
class TaskBase(type):
    def __new__(cls,name,bases,attrs):
        m=type.__new__(cls,name,bases,attrs)
        periodic_registry.register(m.name,m)
        return m
##
## Task handler
##
class Task(object):
    __metaclass__ = TaskBase
    name=None
    description=""
    wait_for=[] # A list of periodic task names which cannot be started concurrenctly
    def __init__(self,sae):
        self.sae=sae
    def execute(self):
        return True
        
