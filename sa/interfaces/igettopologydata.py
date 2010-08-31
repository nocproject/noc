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
from igetmacaddresstable import IGetMACAddressTable
from igetlldpneighbors import IGetLLDPNeighbors
from igetportchannel import IGetPortchannel

class IGetTopologyData(Interface):
    get_mac=BooleanParameter(required=False,default=False)  # Get MAC address table
    get_lldp=BooleanParameter(required=False,default=False) # Get LLDP neighbor information
    
    returns=DictParameter(attrs={
        # Set to true if "mac" is not empty
        "has_mac"    : BooleanParameter(required=False,default=False),
        # Mac address table.
        # Returned only if get_mac is True
        "mac"        : IGetMACAddressTable.returns,
        # Set to true if "lldp_neighbors" is not empty
        "has_lldp"   : BooleanParameter(required=False,default=False),
        # Chassis ID, returned only if get_lldp is set
        "chassis_id" : MACAddressParameter(required=False),
        # LLDP neighbors
        # Returned only if get_lldp is set
        "lldp_neighbors" : IGetLLDPNeighbors.returns,
        # Portchannels
        "portchannels"   : IGetPortchannel.returns,
    })
