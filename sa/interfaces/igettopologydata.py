# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IGetTopologyData interface
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import *
from igetmacaddresstable import IGetMACAddressTable
from igetarp import IGetARP
from igetlldpneighbors import IGetLLDPNeighbors
from igetcdpneighbors import IGetCDPNeighbors
from igetfdpneighbors import IGetFDPNeighbors
from igetspanningtree import IGetSpanningTree
from igetportchannel import IGetPortchannel
from igetinterfaces import IGetInterfaces


class IGetTopologyData(Interface):
    # Get MAC address table
    get_mac = BooleanParameter(required=False, default=False)
    # Get ARP cache
    get_arp = BooleanParameter(required=False, default=False)
    # Get LLDP neighbor information
    get_lldp = BooleanParameter(required=False, default=False)
    # Get CDP neighbor information
    get_cdp = BooleanParameter(required=False, default=False)
    # Get FDP neighbor information
    get_fdp = BooleanParameter(required=False, default=False)
    # Get STP information
    get_stp = BooleanParameter(required=False, default=False)
    # Get interfaces information
    get_interfaces = BooleanParameter(required=False, default=False)

    returns = DictParameter(attrs={
        # Set to true if "mac" is not empty
        "has_mac": BooleanParameter(required=False, default=False),
        # Mac address table.
        # Returned only if get_mac is True
        "mac": NoneParameter() | IGetMACAddressTable.returns,
        # Set to true if "arp" is not empy
        "has_arp": BooleanParameter(required=False, default=False),
        # ARP Cache
        # Returned only if get_arp is True
        "arp": NoneParameter() | IGetARP.returns,
        # Set to true if "lldp_neighbors" is not empty
        "has_lldp": BooleanParameter(required=False, default=False),
        # Chassis ID, returned only if get_lldp is set
        "chassis_id": MACAddressParameter(required=False),
        # LLDP neighbors
        # Returned only if get_lldp is set
        "lldp_neighbors": NoneParameter() | IGetLLDPNeighbors.returns,
        # Set to true if "has_cdp" is not empty
        "has_cdp": BooleanParameter(required=False, default=False),
        # CDP neighbors
        # Returned only if get_cdp is set
        "cdp_neighbors": NoneParameter() | IGetCDPNeighbors.returns,
        # Set to true if "has_fdp" is not empty
        "has_fdp": BooleanParameter(required=False, default=False),
        # CDP neighbors
        # Returned only if get_cdp is set
        "fdp_neighbors": NoneParameter() | IGetFDPNeighbors.returns,
        # Set to true if "stp" is not empty
        "has_stp": BooleanParameter(required=False, default=False),
        # STP Protocol data
        "stp": NoneParameter() | IGetSpanningTree.returns,
        # Portchannels
        "portchannels": IGetPortchannel.returns,
        # Interfaces
        "has_interfaces": BooleanParameter(required=False, default=False),
        "interfaces": NoneParameter() | IGetInterfaces.returns
    })
