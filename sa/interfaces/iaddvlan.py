# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import *

class IAddVlan(Interface):
    vlan_id=VLANIDParameter()
    name=StringParameter()
    tagged_ports=StringListParameter(default=[])
    returns=BooleanParameter()
