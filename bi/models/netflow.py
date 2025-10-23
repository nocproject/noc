# ----------------------------------------------------------------------
# Flows Model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.model import Model
from noc.core.clickhouse.fields import (
    DateField,
    DateTimeField,
    UInt8Field,
    UInt16Field,
    UInt32Field,
    UInt64Field,
    StringField,
    Float64Field,
    ReferenceField,
    IPv4Field,
    # IPv6Field,
)
from noc.core.clickhouse.engines import MergeTree
from noc.core.bi.dictionaries.managedobject import ManagedObject
from noc.core.translation import ugettext as _

NETFLOW_V5 = 5
NETFLOW_V8 = 8
NETFLOW_V9 = 9


class Netflow(Model):
    """
    Netflow collector model
    """

    class Meta:
        db_table = "netflow"
        engine = MergeTree("date", ("date",), primary_keys=("date",))

    date = DateField(description=_("Date"))
    ts = DateTimeField(description=_("Created"))
    managed_object = ReferenceField(ManagedObject, description=_("Object Name"))
    # Coordinates
    x = Float64Field(description=_("Longitude"))
    y = Float64Field(description=_("Latitude"))
    version = UInt8Field(description=_("Flow version"))
    in_bytes = UInt64Field(description=_("Incoming octets"))
    in_pkts = UInt64Field(description=_("Incoming packets"))
    flows = UInt16Field(description=_("Aggregated flows"))
    protocol = UInt8Field(description=_("IP protocol type"))
    src_tos = UInt8Field(description=_("Type of Service byte"))
    tcp_flags = UInt8Field(description=_("TCP flags cumulative byte"))
    src_port = UInt16Field(description=_("TCP/UDP src port number"))
    ipv4_src_addr = IPv4Field(description=_("IPv4 source address"))
    src_mask = UInt8Field(description=_("Number of mask bits in src adr"))
    input_snmp = UInt16Field(description=_("Input interface index"))
    dst_port = UInt16Field(description=_("TCP/UDP dst port number"))
    ipv4_dst_addr = IPv4Field(description=_("IPv4 destination address"))
    dst_mask = UInt8Field(description=_("Number of mask bits in dst adr"))
    output_snmp = UInt16Field(description=_("Output interface index"))
    ipv4_next_hop = IPv4Field(description=_("IPv4 adr of nexthop router"))
    src_as = UInt32Field(description=_("Src BGP AS number"))
    dst_as = UInt32Field(description=_("Dst BGP AS number"))
    bgp_ipv4_next_hop = UInt32Field(description=_("Nexthop router's IP in BGP domain"))
    mul_dst_pkts = UInt64Field(description=_("IP multicast outgoing packet counter"))
    mul_dst_bytes = UInt64Field(description=_("IP multicast outgoing packet counter"))
    last_switched = UInt32Field(description=_("System uptime when last pkt of flow was switched"))
    first_switched = UInt32Field(description=_("System uptime when last pkt of flow was switched"))
    out_bytes = UInt64Field(description=_("Outgoing octets"))
    out_pkts = UInt64Field(description=_("Outgoing packets"))
    min_pkt_lngth = UInt16Field(description=_("Min IP pkt length on inc packets of flow"))
    max_pkt_lngth = UInt16Field(description=_("Max IP pkt length on inc packets of flow"))
    # ipv6_src_addr = IPv6Field(description=_("IPv6 source address"))
    # ipv6_dst_addr = IPv6Field(description=_("IPv6 destination address"))
    # ipv6_src_mask = UInt8Field(description=_("Length of IPv6 source mask in contiguous bits"))
    # ipv6_dst_mask = UInt8Field(description=_("Length of IPv6 destination mask in contiguous bits"))
    # ipv6_flow_label = UInt32Field(description=_("IPv6 flow label as in RFC2460"))
    icmp_type = UInt16Field(description=_("ICMP packet type"))
    mul_igmp_type = UInt8Field(description=_("IGMP packet type"))
    sampling_interval = UInt32Field(description=_("Rate of sampling of packets"))
    sampling_algorithm = UInt8Field(
        description=_(
            "Type of algorithm for sampled netflow: 01 deterministic or 02 random sampling"
        )
    )
    flow_active_timeout = UInt16Field(
        description=_("Timeout value in seconds for active entries in netflow cache")
    )
    flow_inactive_timeout = UInt16Field(
        description=_("Timeout value in seconds for inactive entries in netflow cache")
    )
    engine_type = UInt8Field(description=_("Type of flow switching engine: RP=0, VIP/Linecard=1"))
    engine_id = UInt8Field(description=_("ID number of flow switching engine"))
    total_bytes_exp = UInt32Field(description=_("Counter for bytes exported"))
    total_pkts_exp = UInt32Field(description=_("Counter for pkts exported"))
    total_flows_exp = UInt32Field(description=_("Counter for flows exported"))
    ipv4_src_prefix = UInt32Field(
        description=_("IPv4 source address prefix (Catalyst architecture)")
    )
    ipv4_dst_prefix = UInt32Field(
        description=_("IPv4 destination address prefix (Catalyst architecture)")
    )
    mpls_top_label_type = UInt8Field(description=_("MPLS top label type"))
    mpls_top_label_ip_addr = UInt32Field(
        description=_("Forwarding equivalent class corresponding to MPLS top label")
    )
    flow_sampler_id = UInt8Field(description=_("ID from 'show flow-sampler'"))
    flow_sampler_mode = UInt8Field(description=_("Type of algorithm used for sampling data"))
    flow_sampler_random_interval = UInt32Field(description=_("Packet interval at which to sample"))
    min_ttl = UInt8Field(description=_("Minimum TTL on incoming packets"))
    max_ttl = UInt8Field(description=_("Maximum TTL on incoming packets"))
    ipv4_ident = UInt16Field(description=_("IPv4 identification field"))
    dst_tos = UInt8Field(
        description=_("Type of Service byte setting when exiting outgoing interface")
    )
    in_src_mac = UInt64Field(description=_("Incoming source MAC address"))
    out_dst_mac = UInt64Field(description=_("Outcoming destination MAC address"))
    src_vlan = UInt16Field(description=_("VLAN id associated with ingress interface"))
    dst_vlan = UInt16Field(description=_("VLAN id associated with egress interface"))
    ip_protocol_version = UInt8Field(
        description=_("IP protocol version for IPv4 is 4 and 6 for IPv6. If none, assumed 4")
    )
    direction = UInt8Field(description=_("Flow direction: 0 -- ingress, 1 -- egress flow"))
    # ipv6_next_hop = IPv6Field(description=_("IPv6 address of nexthop router"))
    # bgp_ipv6_next_hop = IPv6Field(description=_("IPv6 address of nexthop router in BGP domain"))
    # ipv6_option_headers = IPv6Field(
    #    description=_("Bit-encoded field identifying IPv6 option headers found in the flow")
    # )
    mpls_label1 = UInt32Field(
        description=_(
            "MPLS label at position 1 in the stack. This comprises 20 bits of MPLS label, 3 EXP (experimental) bits and 1 S (end-of-stack) bit"
        )
    )
    mpls_label2 = UInt32Field(
        description=_(
            "MPLS label at position 2 in the stack. This comprises 20 bits of MPLS label, 3 EXP (experimental) bits and 1 S (end-of-stack) bit"
        )
    )
    mpls_label3 = UInt32Field(
        description=_(
            "MPLS label at position 3 in the stack. This comprises 20 bits of MPLS label, 3 EXP (experimental) bits and 1 S (end-of-stack) bit"
        )
    )
    mpls_label4 = UInt32Field(
        description=_(
            "MPLS label at position 4 in the stack. This comprises 20 bits of MPLS label, 3 EXP (experimental) bits and 1 S (end-of-stack) bit"
        )
    )
    mpls_label5 = UInt32Field(
        description=_(
            "MPLS label at position 5 in the stack. This comprises 20 bits of MPLS label, 3 EXP (experimental) bits and 1 S (end-of-stack) bit"
        )
    )
    mpls_label6 = UInt32Field(
        description=_(
            "MPLS label at position 6 in the stack. This comprises 20 bits of MPLS label, 3 EXP (experimental) bits and 1 S (end-of-stack) bit"
        )
    )
    mpls_label7 = UInt32Field(
        description=_(
            "MPLS label at position 7 in the stack. This comprises 20 bits of MPLS label, 3 EXP (experimental) bits and 1 S (end-of-stack) bit"
        )
    )
    mpls_label8 = UInt32Field(
        description=_(
            "MPLS label at position 8 in the stack. This comprises 20 bits of MPLS label, 3 EXP (experimental) bits and 1 S (end-of-stack) bit"
        )
    )
    mpls_label9 = UInt32Field(
        description=_(
            "MPLS label at position 9 in the stack. This comprises 20 bits of MPLS label, 3 EXP (experimental) bits and 1 S (end-of-stack) bit"
        )
    )
    mpls_label10 = UInt32Field(
        description=_(
            "MPLS label at position 10 in the stack. This comprises 20 bits of MPLS label, 3 EXP (experimental) bits and 1 S (end-of-stack) bit"
        )
    )
    in_dst_mac = UInt64Field(description=_("Incoming destination MAC address"))
    out_src_mac = UInt64Field(description=_("Outcoming source MAC address"))
    if_name = StringField(description=_("Shortened interface name i.e.: 'FE1/0'"))
    if_desc = StringField(description=_("Full interface name i.e.: 'FastEthernet 1/0'"))
    sampler_name = StringField(description=_("Name of the flow sampler"))
    in_permanent_bytes = UInt32Field(description=_("Running byte counter for a permanent flow"))
    in_permanent_pkts = UInt32Field(description=_("Running packet counter for a permanent flow"))
    fragment_offset = UInt16Field(
        description=_("The fragment-offset value from fragmented IP packets")
    )
    forwarding_status = UInt8Field(
        description=_(
            "Forwarding status is encoded on 1 byte with the 2 left bits giving the status and the 6 remaining bits giving the reason code."
        )
    )
    mpls_pal_rd = UInt64Field(description=_("MPLS PAL Route Distinguisher"))
    mpls_prefix_len = UInt8Field(
        description=_("Number of consecutive bits in the MPLS prefix length")
    )
    src_traffic_index = UInt32Field(description=_("BGP Policy Accounting Source Traffic Index"))
    dst_traffic_index = UInt32Field(
        description=_("BGP Policy Accounting Destination Traffic Index")
    )
    application_description = StringField(description=_("Application description"))
    application_tag = UInt16Field(
        description=_("8 bits of engine ID, followed by n bits of classification")
    )
    application_name = StringField(description=_("Name associated with a classification"))
    postipDiffServCodePoint = UInt8Field(
        description=_(
            "The value of a Differentiated Services Code Point (DSCP) encoded in the Differentiated Services Field, after modification"
        )
    )
    replication_factor = UInt32Field(description=_("Multicast replication factor"))

    src4_xlt_ip = IPv4Field(description=_("IPv4 post NAT src address"))
    src_xlt_port = UInt16Field(description=_("TCP/UDP port NAT src port number"))
    dst4_xlt_ip = IPv4Field(description=_("IPv4 post NAT dst address"))
    dst_xlt_port = UInt16Field(description=_("TCP/UDP port NAT dst port number"))
