# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Models for "sa" module
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
## Django modules
## Third-party modules
## NOC modules
from noc.sa.profiles import profile_registry
from noc.sa.script import script_registry
##
## Register objects
##
profile_registry.register_all()
script_registry.register_all()

## Import models
from administrativedomain import AdministrativeDomain
from activator import Activator
from managedobject import ManagedObject, ManagedObjectAttribute
from managedobjectselector import (ManagedObjectSelector,
                                   ManagedObjectSelectorByAttribute)
from useraccess import UserAccess
from groupaccess import GroupAccess
from reducetask import ReduceTask
from maptask import MapTask
from commandsnippet import CommandSnippet
from activatorcapabilitiescache import ActivatorCapabilitiesCache
from mrtconfig import MRTConfig
from failedscriptlog import FailedScriptLog


##
## SAE services shortcuts
##
def sae_refresh_event_filter(object):
    """
    Refresh event filters for all activators serving object
    
    :param object: Managed object
    :type object: ManagedObject instance
    """
    def reduce_notify(task):
        mt = task.maptask_set.all()[0]
        if mt.status == "C":
            return mt.script_result
        return False
    
    t = ReduceTask.create_task("SAE", reduce_notify, {},
                               "notify", {"event": "refresh_event_filter",
                                          "object_id": object.id}, 1)
    #return t.get_result()
