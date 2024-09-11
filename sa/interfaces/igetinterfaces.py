# ---------------------------------------------------------------------
# IGetInterfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.interface.base import BaseInterface
from .base import (
    ListOfParameter,
    DictParameter,
    DictListParameter,
    StringListParameter,
    InterfaceNameParameter,
    MACAddressParameter,
    VLANIDParameter,
    VLANStackParameter,
    RDParameter,
    IPParameter,
    IPv4PrefixParameter,
    IPv6PrefixParameter,
    StringParameter,
    BooleanParameter,
    IntParameter,
    LabelListParameter,
)


class IGetInterfaces(BaseInterface):
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

    L2 Switchport (untagged access port in VLANID)
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

    L2 Switchport (tagged port in VLANS)
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

    L2 Ethernet Services (VLAN Mappings)
    ------------------------------------
    forwarding_instance:
        forwarding_instance = "default"
        type = "ip"
        interfaces:
            name = physical port name
            type = "physical"
            mac = interface mac address
            subinterfaces:
                name = interface name (same as physical name for most platforms)
                enabled_afi = ["ES"]
                input_vlan_map = [{
                    stack: 0 | 1 | 2  # Untagged | 802.1Q | Q-in-Q
                    macs: [...mac addresses list...]
                    inner_vlans: [...vlans list...]
                    outer_vlans: [...vlans list...]
                    rewrite: [
                        {
                            op: "pop" | "push" | "swap",
                            vlan: vlan id
                        },
                        ...
                    ]
                }]
                output_vlan_map = ... like input_vlan_map ...

    * Untagged port in vlan 100
    input_vlan_map = [{
        stack: 0,
        rewrite: [{
            op: "push",
            vlan: 100
        }]
    }]
    output_vlan_map = [{
        stack: 1,
        inner_vlans: [100]
        rewrite: [{
            op: "pop"
        }]
    }]
    * Tagged vlans 100-200, untagged vlan 5
    input_vlan_map = [
        {
            stack: 0,
            rewrite: [{
                op: "push",
                vlan: 5
            }]
        },
        {
            stack: 1,
            inner_vlans: [100, .., 200]
        }
    ]
    output_vlan_map = [
        {
            stack: 1,
            inner_vlans: [5],
            rewrite: [{
                op: "pop"
            }]
        },
        {
            stack: 1,
            inner_vlans: [100, .., 200]
        }
    ]
    * Tagged 100-200, push outer vlan 10
    input_vlan_map = [{
        stack: 1,
        inner_vlans: [100, .., 200],
        rewrite: [{
            op: "push",
            vlan: 10
        }]
    }]
    output_vlan_map = [{
        stack: 2,
        outer_vlans: [10],
        inner_vlans: [100, .., 200],
        rewrite: [{
            op: "pop"
        }]
    }]

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
            enabled_protoocols = ["LACP"]
            aggregated_interface = "if1"

            name = if3
            type = "physical"
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
            type = "physical"
            enabled_protocols = ["LACP"]
            aggregated_interface = "if1"

            name = if3
            type = "physical"
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

    returns = DictListParameter(
        attrs={
            # Name of the forwarding instance
            "forwarding_instance": StringParameter(default="default"),
            "virtual_router": StringParameter(required=False),
            "type": StringParameter(
                choices=["table", "bridge", "vrf", "vll", "vpls", "evpn", "vxlan"],
                default="table",
                aliases={"ip": "table", "VRF": "vrf", "VPLS": "vpls", "VLL": "vll"},
            ),
            "rd": RDParameter(required=False),
            # Route-target export for VRF
            "rt_export": ListOfParameter(element=RDParameter(), required=False),
            # Route-target import for VRF
            "rt_import": ListOfParameter(element=RDParameter(), required=False),
            # Refer IGetMPLSVPN.vpn_id for details
            "vpn_id": StringParameter(required=False),
            "interfaces": DictListParameter(
                attrs={
                    "name": InterfaceNameParameter(),
                    # Default interface name,
                    # in case the `name` can be configured (i.e. RouterOS)
                    "default_name": StringParameter(required=False),
                    "type": StringParameter(
                        choices=[
                            "physical",
                            "SVI",
                            "aggregated",
                            "loopback",
                            "management",
                            "null",
                            "tunnel",
                            "other",
                            "template",
                            "dry",  # Dry contact
                            "internal",
                            "unknown",
                            "physical",
                        ]
                    ),
                    "admin_status": BooleanParameter(default=False),
                    "oper_status": BooleanParameter(default=False),
                    "aggregated_interface": InterfaceNameParameter(
                        required=False
                    ),  # Not empty for portchannel members
                    # L2 protocols enabled on interface
                    "enabled_protocols": StringListParameter(
                        choices=[
                            "LACP",
                            "LLDP",
                            "CDP",
                            "UDLD",
                            "CTP",
                            "GVRP",
                            "VTP",
                            "STP",
                            "BFD",
                            "OAM",
                            "NDP",
                            "DRY_NO",  # Dry contact, Normal Open
                            "DRY_NC",  # Dry contact, Normal Closed
                            "DRY_PULSE",  # Dry contact, pulse mode
                        ],
                        required=False,
                    ),
                    "description": StringParameter(required=False),
                    "mac": MACAddressParameter(required=False),
                    "snmp_ifindex": IntParameter(required=False),
                    # noc::interface::role::uni/nni
                    # noc::topology::direction::uplink
                    "hints": LabelListParameter(
                        required=False,
                        default_scope="noc::interface::hints",
                        allowed_scopes=[
                            "noc::topology::direction",
                            "noc::interface::role",
                            "noc::interface::hints",
                            "noc::interface::port_group",
                            "technology::pon",
                            "technology::ethernet",
                            "technology::dsl",
                            "technology::radio",
                        ],
                    ),
                    "subinterfaces": ListOfParameter(
                        element=DictParameter(
                            attrs={
                                "name": InterfaceNameParameter(),
                                "admin_status": BooleanParameter(default=False),
                                "oper_status": BooleanParameter(default=False),
                                "mtu": IntParameter(required=False),
                                "description": StringParameter(required=False),
                                "mac": MACAddressParameter(required=False),
                                "vlan_ids": VLANStackParameter(required=False),
                                # Enabled address families
                                "enabled_afi": StringListParameter(
                                    choices=[
                                        "IPv4",
                                        "IPv6",
                                        "ISO",
                                        "MPLS",
                                        "BRIDGE",
                                        "ES",
                                        "ATM",
                                        "iSCSI",
                                    ],
                                    required=False,
                                ),  # @todo: make required
                                "ipv4_addresses": ListOfParameter(
                                    element=IPv4PrefixParameter(), required=False
                                ),  # enabled_afi = [... IPv4 ...]
                                "ipv6_addresses": ListOfParameter(
                                    element=IPv6PrefixParameter(), required=False
                                ),  # enabled_afi = [... IPv6 ...]
                                "iso_addresses": StringListParameter(
                                    required=False
                                ),  # enabled_afi = [... ISO ...]
                                "vpi": IntParameter(
                                    required=False
                                ),  # enabled afi = [ ... ATM ... ]
                                "vci": IntParameter(
                                    required=False
                                ),  # enabled afi = [ ... ATM ... ]
                                # Enabled L3 protocols
                                "enabled_protocols": StringListParameter(
                                    choices=[
                                        "ISIS",
                                        "OSPF",
                                        "RIP",
                                        "EIGRP",
                                        "OSPFv3",
                                        "BGP",
                                        "LDP",
                                        "RSVP",
                                        "PIM",
                                        "DVMRP",
                                        "IGMP",
                                        "VRRP",
                                        "SRRP",
                                    ],
                                    required=False,
                                ),
                                "untagged_vlan": VLANIDParameter(
                                    required=False
                                ),  # enabled_afi = [BRIDGE]
                                "tagged_vlans": ListOfParameter(
                                    element=VLANIDParameter(), required=False
                                ),  # enabled_afi = [BRIDGE]
                                # Input VLAN tag processing, enabled_afi = [ES]
                                "input_vlan_map": DictListParameter(
                                    attrs={
                                        # VLAN stack depth to match
                                        "stack": IntParameter(min_value=0, max_value=2, default=0),
                                        # outer VLAN list to match (stack == 2)
                                        "outer_vlans": ListOfParameter(
                                            element=VLANIDParameter(), required=False
                                        ),
                                        # inner VLAN list to match (stack in (1, 2))
                                        "inner_vlans": ListOfParameter(
                                            element=VLANIDParameter(), required=False
                                        ),
                                        # Tag rewrite operations list
                                        "rewrite": DictListParameter(
                                            attrs={
                                                # refer to noc.core.vlanmap documentation
                                                "op": StringParameter(
                                                    choices=["pop", "push", "swap", "drop"]
                                                ),
                                                "vlan": VLANIDParameter(required=False),
                                            },
                                            required=False,
                                        ),
                                    },
                                    required=False,
                                ),
                                # Output VLAN tag processing, enabled_afi = [ES]
                                "output_vlan_map": DictListParameter(
                                    attrs={
                                        # VLAN stack depth to match
                                        "stack": IntParameter(min_value=0, max_value=2, default=0),
                                        # outer VLAN list to match (stack == 2)
                                        "outer_vlans": ListOfParameter(
                                            element=VLANIDParameter(), required=False
                                        ),
                                        # inner VLAN list to match (stack in (1, 2))
                                        "inner_vlans": ListOfParameter(
                                            element=VLANIDParameter(), required=False
                                        ),
                                        # Tag rewrite operations list
                                        "rewrite": DictListParameter(
                                            attrs={
                                                # refer to noc.core.vlanmap documentation
                                                "op": StringParameter(
                                                    choices=["pop", "push", "swap", "drop"]
                                                ),
                                                "vlan": VLANIDParameter(required=False),
                                            },
                                            required=False,
                                        ),
                                    },
                                    required=False,
                                ),
                                # Dynamic vlans, enabled_afi = [ES or BRIDGE]
                                "dynamic_vlans": DictListParameter(
                                    attrs={
                                        "vlan": VLANIDParameter(),
                                        "service": StringParameter(choices=["voice", "mvr"]),
                                    },
                                    required=False,
                                ),
                                "ip_unnumbered_subinterface": InterfaceNameParameter(
                                    required=False
                                ),
                                "snmp_ifindex": IntParameter(required=False),
                                # Tunnel services
                                "tunnel": DictParameter(
                                    required=False,
                                    attrs={
                                        "type": StringParameter(
                                            choices=[
                                                "GRE",
                                                "IPIP",
                                                "IPsec",
                                                "PPTP",
                                                "L2TP",
                                                "PPPOE",
                                                "PPP",
                                                "SSTP",
                                                "EOIP",
                                                "SLIP",
                                            ]
                                        ),
                                        "local_address": IPParameter(required=False),
                                        "remote_address": IPParameter(required=False),
                                    },
                                ),
                            }
                        )
                    ),
                }
            ),
        }
    )
