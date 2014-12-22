# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IGetInterfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
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
                enabled_afi = ["IPv4", "IPv6"]
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
                enabled_afi = ["IPv4"]
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
                enabled_afi = ["BRIDGE"]
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
                enabled_afi = ["BRIDGE"]
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
                enabled_afi = ["IPv4"]
                ipv4_addresses = [list of VLAN1 addresses]

                name = interface name.VLAN2 (for most platforms)
                vlan_ids = [VLAN2]
                enabled_afi = ["IPv4"]
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
                enabled_afi = ["IPv4"]
                ipv4_addresses = list of IPv4 addresses
    
            name = if2
            type = "physical"
            is_lacp = True  # @todo: Deprecated
            enabled_protoocols = ["LACP"]
            aggregated_interface = "if1"

            name = if3
            type = "physical"
            is_lacp = True  # @todo: Deprecated
            enabled_protoocols = ["LACP"]
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
                enabled_afi = ["BRIDGE"]
                tagged_vlans = list of tagged vlans

            name = if2
            type = "aggregate"
            enabled_protocols = ["LACP"]
            aggregated_interface = "if1"

            name = if3
            type = "aggregate"
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
                enabled_afi = ["IPv4"]
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
                enabled_afi = ["IPv4"]
                ipv4_addresses = List of VLAN2 addresses in VRF1

    DSLAM routed port
    -----------------
    forwarding_instance:
    forwarding_instance = "default"
    type = "ip"
    interfaces:
        name = physical port name
        type = "physical"
        subinterfaces:
            name = interface name (same as physical name for most platforms)
            enabled_afi = ["IPv4", "IPv6", "ATM"]
            ipv4_addresses = list of IPv4 addresses
            ipv6_addresses = list of IPv6 addresses
            vpi = port vpi
            vci = port vci

    DSLAM bridge port
    -----------------
    forwarding_instance:
    forwarding_instance = "default"
    type = "ip"
    interfaces:
        name = physical port name
        type = "physical"
        subinterfaces:
            name = interface name (same as physical name for most platforms)
            enabled_afi = ["BRIDGE", "ATM"]
            untagged_vlan = untagged vlan, if any
            tagged_vlans = list of tagged vlans, if any
            vpi = port vpi
            vci = port vci

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
            # L2 protocols enabled on interface
            "enabled_protocols": ListOfParameter(
                element=StringParameter(choices=[
                    "LACP", "LLDP", "CDP", "UDLD", "CTP", "GVRP", "VTP", "STP"
                ]), required=False),
            "description": StringParameter(required=False),
            "mac": MACAddressParameter(required=False),
            "snmp_ifindex": IntParameter(required=False),
            "subinterfaces": ListOfParameter(element=DictParameter(attrs={
                "name": InterfaceNameParameter(),
                "admin_status": BooleanParameter(default=False),
                "oper_status": BooleanParameter(default=False),
                "mtu": IntParameter(required=False),
                "description": StringParameter(required=False),
                "mac": MACAddressParameter(required=False),
                "vlan_ids": VLANStackParameter(required=False),
                # Enabled address families
                "enabled_afi": ListOfParameter(
                    element=StringParameter(choices=[
                        "IPv4", "IPv6", "ISO", "MPLS", "BRIDGE", "ATM"
                    ]), required=False  # #todo: make required
                ),
                "ipv4_addresses": ListOfParameter(element=IPv4PrefixParameter(), required=False),  # enabled_afi = [... IPv4 ...]
                "ipv6_addresses": ListOfParameter(element=IPv6PrefixParameter(), required=False),  # enabled_afi = [... IPv6 ...]
                "iso_addresses": ListOfParameter(element=StringParameter(), required=False),  #   # enabled_afi = [... ISO ...]
                "vpi": IntParameter(required=False),  # enabled afi = [ ... ATM ... ]
                "vci": IntParameter(required=False),  # enabled afi = [ ... ATM ... ]
                # Enabled L3 protocols
                "enabled_protocols": ListOfParameter(
                                element=StringParameter(choices=[
                                    "ISIS", "OSPF", "RIP", "EIGRP", "OSPFv3",
                                    "BGP",
                                    "LDP", "RSVP", "NDP",
                                    "PIM", "DVMRP", "IGMP", "VRRP", "SRRP"
                                ]), required=False),
                "untagged_vlan": VLANIDParameter(required=False),  # enabled_afi = [BRIDGE]
                "tagged_vlans": ListOfParameter(element=VLANIDParameter(), required=False),  # enabled_afi = [BRIDGE]
                "ip_unnumbered_subinterface": InterfaceNameParameter(required=False),
                "snmp_ifindex": IntParameter(required=False),
                # Tunnel services
                "tunnel": DictParameter(required=False, attrs={
                    "type": StringParameter(choices=[
                        "GRE", "IPIP", "IPsec", "PPTP", "L2TP", "PPPOE", "PPP"
                    ]),
                    "local_address": IPParameter(required=False),
                    "remote_address": IPParameter(required=False)
                })
            }))
        }))
    }))
