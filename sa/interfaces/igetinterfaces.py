# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IGetInterfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from base import *
##
## IGetInterfaces
##
class IGetInterfaces(Interface):
    returns=ListOfParameter(element=DictParameter(attrs={
            # Name of the forwarding instance
            "forwarding_instance" : StringParameter(default="default"),
            "virtual_router"      : StringParameter(required=False),
            "type"                : StringParameter(choices=["ip", "bridge", "VRF", "VPLS", "VLL"], default="ip"),
            "interfaces"          : ListOfParameter(element=DictParameter(attrs={
                    "name"  : InterfaceNameParameter(),
                    "type"  : StringParameter(choices=["physical", "SVI", "aggregated", "loopback", "management"]),
                    "admin_status"         : BooleanParameter(default=False),
                    "oper_status"          : BooleanParameter(default=False),
                    "aggregated_interface" : InterfaceNameParameter(required=False), # Not empty for portchannel members
                    "is_lacp"              : BooleanParameter(required=False),
                    "description"          : StringParameter(required=False),
                    "mac"                  : MACAddressParameter(required=False),
                    "subinterfaces" : ListOfParameter(element=DictParameter(attrs={
                            "name"           : InterfaceNameParameter(),
                            "admin_status"   : BooleanParameter(default=False),
                            "oper_status"    : BooleanParameter(default=False),
                            "description"    : StringParameter(required=False),
                            "mac"            : MACAddressParameter(required=False),
                            "vlan_ids"       : ListOfParameter(element=VLANIDParameter(), required=False),
                            "is_ipv4"        : BooleanParameter(required=False),
                            "is_ipv6"        : BooleanParameter(required=False),
                            "is_iso"         : BooleanParameter(required=False),
                            "is_mpls"        : BooleanParameter(required=False),
                            "is_bridge"      : BooleanParameter(required=False),
                            "ipv4_addresses" : ListOfParameter(element=IPv4PrefixParameter(), required=False),
                            "ipv6_addresses" : ListOfParameter(element=IPv6PrefixParameter(), required=False),
                            "iso_addresses"  : ListOfParameter(element=StringParameter(),     required=False),
                            "is_isis"        : BooleanParameter(required=False),
                            "is_ospf"        : BooleanParameter(required=False),
                            "is_rip"         : BooleanParameter(required=False),
                            "is_bgp"         : BooleanParameter(required=False),
                            "is_eigrp"       : BooleanParameter(required=False),
                            "untagged_vlan"  : VLANIDParameter(required=False),
                            "tagged_vlans"   : ListOfParameter(element=VLANIDParameter(), required=False),
                            "ip_unnumbered_subinterface" : InterfaceNameParameter(required=False),
                            "snmp_ifindex"   : IntParameter(required=False)
                            }))
                    })),
        }))
