# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IGetTopologyData interface
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import *

class IGetTopologyData(Interface):
    get_mac=BooleanParameter(required=False,default=False) # Get MAC address table
    
    returns=DictParameter(attrs={
        # Set to true if "mac" is not empty
        "has_mac" : BooleanParameter(required=False,default=False),
        # Mac address table.
        # Returned only if get_mac is True
        "mac"     : ListOfParameter(element=DictParameter(attrs={"vlan_id"    : VLANIDParameter(),
                                                             "mac"        : MACAddressParameter(),
                                                             "interfaces" : StringListParameter(),
                                                             "type"       : StringParameter(), # choices=["D","S"]
                                                             })),
    })
