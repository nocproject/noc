import datetime,os
from noc.lib.registry import Registry

##
##
##
class PeriodicRegistry(Registry):
    name="PeriodicRegistry"
    subdir="periodics"
    classname="Task"
    
periodic_registry=PeriodicRegistry()

##
##
##
class TaskBase(type):
    def __new__(cls,name,bases,attrs):
        m=type.__new__(cls,name,bases,attrs)
        periodic_registry.register(m.name,m)
        return m

##
##
##
##
class Task(object):
    __metaclass__ = TaskBase
    name=None
    description=""
    def execute(self):
        return True