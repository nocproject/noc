# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IGetInterfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from base import *


class IGetInterfaces(Interface):
    """
    IGetInterfaces.
    
    Common usage scenarios

    L3 IPv4/IPv6 port.
    ------------------
    forwarding_instance:
        forwarding_instance = "default"
        type = "ip"
        interfaces:
            name = physical port name
            type = "physical"
            mac = interface mac address
            subinterfaces:
                name = interface name (same as physical name for most platforms)
                is_ipv4 = True
                is_ipv6 = True
                ipv4_addresses = list of IPv4 addresses
                ipv6_addresses = list of IPv6 addresses

    L3 IP Unnumbered IPv4
    ---------------------
    forwarding_instance:
        forwarding_instance = "default"
        type = "ip"
        interfaces:
            name = physical port name
            type = "physical"
            mac = interface mac address
            subinterfaces:
                name = interface name (same as physical name for most platforms)
                is_ipv4 = True
                ip_unnumbered_subinterface = subinterface name to borrow an address

    L3 Switchport (untagged access port in VLANID)
    ----------------------------------------------
    forwarding_instance:
        forwarding_instance = "default"
        type = "ip"
        interfaces:
            name = physical port name
            type = "physical"
            mac = interface mac address
            subinterfaces:
                name = interface name (same as physical name for most platforms)
                is_bridge = True
                untagged_vlan = VLANID

    L3 Switchport (tagged port in VLANS)
    ----------------------------------------------
    forwarding_instance:
        forwarding_instance = "default"
        type = "ip"
        interfaces:
            name = physical port name
            type = "physical"
            mac = interface mac address
            subinterfaces:
                name = interface name (same as physical name for most platforms)
                is_bridge = True
                tagged_vlans = VLANS (list)
    
    L3-terminated 802.1Q trunk (in VLAN1 and VLAN2)
    -----------------------------------------------
    forwarding_instance:
        forwarding_instance = "default"
        type = "ip"
        interfaces:
            name = physical port name
            type = "physical"
            mac = interface mac address
            subinterfaces:
                name = interface name.VLAN1 (for most platforms)
                vlan_ids = [VLAN1]
                is_ipv4 = True
                ipv4_addresses = [list of VLAN1 addresses]
                
                name = interface name.VLAN2 (for most platforms)
                vlan_ids = [VLAN2]
                is_ipv4 = True
                ipv4_addresses = [list of VLAN2 addresses]
    
    L3 portchannel (if1 is aggregated interface of if2 and if3 with LACP)
    -----------------------------------------------------------
    forwarding_instance:
        forwarding_instance = "default"
        type = "ip"
        interfaces:
            name = if1
            type = "aggregated"
            subinterfaces:
                name = interface name (same as parent for most platforms)
                is_ipv4 = True
                ipv4_addresses = list of IPv4 addresses
    
            name = if2
            type = "aggregate"
            is_lacp = True
            aggregated_interface = "if1"
            
            name = if3
            type = "aggregate"
            is_lacp = True
            aggregated_interface = "if1"
    
    L2 portchannel, tagged (if1 is aggregated interface of if2(LACP) and if3(static))
    ---------------------------------------------------------------------------------
    forwarding_instance:
        forwarding_instance = "default"
        type = "ip"
        interfaces:
            name = if1
            type = "aggregated"
            subinterfaces:
                name = interface name (same as parent for most platforms)
                is_bridge = True
                tagged_vlans = list of tagged vlans
    
            name = if2
            type = "aggregate"
            is_lacp = True
            aggregated_interface = "if1"
            
            name = if3
            type = "aggregate"
            is_lacp = False
            aggregated_interface = "if1"
    
    802.1Q trunk. (VLAN1 is L3, VLAN2 in VRF1)
    -----------------------------------------
    forwarding_instance:
        forwarding_instance = "default"
        type = "ip"
        interfaces:
            name = interface name
            type = "physical"
            subinterfaces:
                name = interface name.VLAN1 (for most platforms)
                vlan_ids = [VLAN1]
                is_ipv4 = True
                ipv4_addresses = List of VLAN1 addresses

        forwarding_instance = "VRF1"
        type = "vrf"
        @todo RD
        interfaces:
            name = interface name
            type = "physical"
            subinterfaces:
                name = interface name.VLAN2 (for most platforms)
                vlan_ids = [VLAN2]
                is_ipv4 = True
                ipv4_addresses = List of VLAN2 addresses in VRF1
                
    """
    returns = ListOfParameter(element=DictParameter(attrs={
        # Name of the forwarding instance
        "forwarding_instance": StringParameter(default="default"),
        "virtual_router": StringParameter(required=False),
        "type": StringParameter(choices=["ip", "bridge", "VRF",
                                         "VPLS", "VLL"], default="ip"),
        "rd": RDParameter(required=False),
        "interfaces": ListOfParameter(element=DictParameter(attrs={
            "name": InterfaceNameParameter(),
            "type": StringParameter(choices=["physical", "SVI", "aggregated",
                                             "loopback", "management",
                                             "null", "tunnel", "other", "unknown"]),
            "admin_status": BooleanParameter(default=False),
            "oper_status": BooleanParameter(default=False),
            "aggregated_interface": InterfaceNameParameter(required=False), # Not empty for portchannel members
            "is_lacp": BooleanParameter(required=False),
            "description": StringParameter(required=False),
            "mac": MACAddressParameter(required=False),
            "subinterfaces": ListOfParameter(element=DictParameter(attrs={
                "name": InterfaceNameParameter(),
                "admin_status": BooleanParameter(default=False),
                "oper_status": BooleanParameter(default=False),
                "description": StringParameter(required=False),
                "mac": MACAddressParameter(required=False),
                "vlan_ids": ListOfParameter(element=VLANIDParameter(), required=False),
                "is_ipv4": BooleanParameter(required=False),
                "is_ipv6": BooleanParameter(required=False),
                "is_iso": BooleanParameter(required=False),
                "is_mpls": BooleanParameter(required=False),
                "is_bridge": BooleanParameter(required=False),
                "ipv4_addresses": ListOfParameter(element=IPv4PrefixParameter(), required=False),
                "ipv6_addresses": ListOfParameter(element=IPv6PrefixParameter(), required=False),
                "iso_addresses": ListOfParameter(element=StringParameter(), required=False),
                "is_isis": BooleanParameter(required=False),
                "is_ospf": BooleanParameter(required=False),
                "is_rsvp": BooleanParameter(required=False),
                "is_ldp": BooleanParameter(required=False),
                "is_rip": BooleanParameter(required=False),
                "is_bgp": BooleanParameter(required=False),
                "is_eigrp": BooleanParameter(required=False),
                "untagged_vlan": VLANIDParameter(required=False),
                "tagged_vlans": ListOfParameter(element=VLANIDParameter(), required=False),
                "ip_unnumbered_subinterface": InterfaceNameParameter(required=False),
                "snmp_ifindex": IntParameter(required=False)
            }))
        })),
        }))
