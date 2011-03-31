# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IConfigDiffFilter
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import *
##
## IConfigDiffFilter interface
##
class IConfigDiffFilter(Interface):
    managed_object=InstanceOfParameter("ManagedObject")
    config=StringParameter()
    returns=StringParameter()
