# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IGetSpanningTree
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import *
##
class IGetSpanningTree(Interface):
    returns=DictParameter(attrs={
        # Spanning-tree mode. Must be one of:
        #    None        - Spanning-tree is disabled
        #    STP         - IEEE 802.1d Spanning Tree Protocol
        #    RSTP        - IEEE 802.1w Rapid Spanning Tree Protocol
        #    MSTP        - IEEE 802.1Q-2003 Multiple Spanning Tree Protocol
        #    PVST+       - Per-Vlan Spanning Tree Plus - Cisco extension to STP
        #    rapid-PVST+ - Rapind Per-Vlan Spanning Tree Plus - Cisco extension to RSTP
        "mode"      : StringParameter(choices=["STP","RSTP","MSTP","PVST+","rapid-PVST+"]),
        #
        "configuration" : DictParameter(attrs={
            # MSTP-specific configuration
            "MSTP" : DictParameter(attrs={
                # MST Region
                "region"  : StringParameter(),
                # MST Revision
                "revision": IntParameter(),
            },required=False),
        },required=False),
        # List of STP instances.
        # For mode==None, list must be empty
        # For STP and RSTP, only one instance id 0 must be present
        # For PVST mode - instance id is vlan id
        # For MSTP mode - instance id is MSTP instance id
        "instances" : ListOfParameter(element=DictParameter(attrs={
            # Instnce ID
            "id"      : IntParameter(),
            # VLAN IDs mapped to instance.
            # Must be 1-4095 for STP and RSTP
            # IDs mapped to particular instance for MSTP
            # AND single VLAN id for *PVST+
            "vlans"   : VLANIDMapParameter(),
            # Root bridge id, equal to bridge_id for root bridge
            "root_id" : MACAddressParameter(),
            # Root bridge priority
            "root_priority" : IntParameter(),
            # Bridge ID
            "bridge_id" : MACAddressParameter(),
            # Bridge priority
            "bridge_priority" : IntParameter(),
            # Interfaces
            "interfaces" : ListOfParameter(element=DictParameter(attrs={
                # Interface name
                "interface" : InterfaceNameParameter(),
                # Interface status
                "status"    : StringParameter(choices=["FWD","DIS","BLK"]),
                # Interface role
                "role"      : StringParameter(choices=["ROOT","DESG","ALTN","BACK","DIS"]),
                # Local port id
                "port_id"   : StringParameter(),
                # Port priority
                "priority"  : IntParameter(),
                # Port cost
                "cost"      : IntParameter(),
                # Designated bridge ID
                "designated_bridge_id" : MACAddressParameter(),
                # Designated bridge priority
                "designated_bridge_priority" : IntParameter(),
                # Designated port id
                "designated_port_id" : StringParameter(),
                # Link Type
                "link_type" : StringParameter(choices=["P2P"]),
                # MSTP EdgePort
                "edge"      : BooleanParameter(),
            }))
        })),
    })