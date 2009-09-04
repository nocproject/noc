# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import *

class ISyncVlans(Interface):
    vlans=ListOfParameter(element=DictParameter(attrs={"vlan_id":VLANIDParameter(),
                                                       "name":StringParameter(required=False)}))
    tagged_ports=StringListParameter(default=[])
    returns=DictParameter(attrs={"created" : ListOfParameter(element=VLANIDParameter()),
                                 "removed" : ListOfParameter(element=VLANIDParameter())})
