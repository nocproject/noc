# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import *

class IRemoveVlan(Interface):
    vlan_id=VLANIDParameter()
    returns=BooleanParameter()
