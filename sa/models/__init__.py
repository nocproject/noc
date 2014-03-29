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
from collector import Collector
from managedobjectprofile import ManagedObjectProfile
from authprofile import AuthProfile
from managedobject import ManagedObject, ManagedObjectAttribute
from managedobjectselector import (ManagedObjectSelector,
                                   ManagedObjectSelectorByAttribute)
from objectnotification import ObjectNotification
from useraccess import UserAccess
from groupaccess import GroupAccess
from reducetask import ReduceTask
from maptask import MapTask
from commandsnippet import CommandSnippet
from activatorcapabilitiescache import ActivatorCapabilitiesCache
from mrtconfig import MRTConfig
from failedscriptlog import FailedScriptLog
##
## Post-initialization
##
import post_init
