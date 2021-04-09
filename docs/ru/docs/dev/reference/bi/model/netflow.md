# Flows model

## Table Structure

| Setting    | Value                                       |
| ---------- | ------------------------------------------- |
| Table Name | flows                                       |
| Engine     | MergeTree(date, (managed_object, ts), 8192) |

| Field                          | Data Type             | Description                                                                                                                    |
| ------------------------------ | --------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| date                           | Date                  | Date                                                                                                                           |
| ts                             | DateTime              | Created                                                                                                                        |
| managed_object                 | UInt64                | Object Name                                                                                                                    |
| x                              | Float64               | Longitude (Coordinates)                                                                                                        |
| y                              | Float64               | Latitude (Coordinates)                                                                                                         |
| version                        | UInt8                 | Flow version                                                                                                                   |
| in_bytes                       | UInt64                | Incoming octets                                                                                                                |
| in_pkts                        | UInt64                | Incoming packets                                                                                                               |
| flows                          | UInt16                | Aggregated flows                                                                                                               |
| protocol                       | UInt8                 | IP protocol type                                                                                                               |
| src_tos                        | UInt8                 | Type of Service byte                                                                                                           |
| tcp_flags                      | UInt8                 | TCP flags cumulative byte                                                                                                      |
| l4_src_port                    | UInt8                 | TCP/UDP src port number                                                                                                        |
| ipv4_src_addr                  | IPv4                  | IPv4 source address                                                                                                            |
| src_mask                       | UInt8                 | Number of mask bits in src adr                                                                                                 |
| input_snmp                     | UInt16                | Input interface index                                                                                                          |
| ipv4_dst_port                  | UInt8                 | TCP/UDP dst port number                                                                                                        |
| ipv4_dst_addr                  | IPv4                  | IPv4 destination address                                                                                                       |
| dst_mask                       | UInt8                 | Number of mask bits in dst adr                                                                                                 |
| output_snmp                    | UInt16                | Output interface index                                                                                                         |
| ipv4_next_hop                  | IPv4                  | IPv4 adr of nexthop router                                                                                                     |
| src_as                         | UInt32                | Src BGP AS number                                                                                                              |
| dst_as                         | UInt32                | Dst BGP AS number                                                                                                              |
| bgp_ipv4_next_hop              | UInt32                | Nexthop router's IP in BGP domain                                                                                              |
| mul_dst_pkts                   | UInt64                | IP multicast outgoing packet counter                                                                                           |
| mul_dst_bytes                  | UInt64                | IP multicast outgoing packet counter                                                                                           |
| last_switched                  | UInt32                | System uptime when last pkt of flow was switched                                                                               |
| first_switched                 | UInt32                | System uptime when last pkt of flow was switched                                                                               |
| out_bytes                      | UInt64                | Outgoing octets                                                                                                                |
| out_pkts                       | UInt64                | Outgoing packets                                                                                                               |
| min_pkt_lngth                  | UInt16                | Min IP pkt length on inc packets of flow                                                                                       |
| max_pkt_lngth                  | UInt16                | Max IP pkt length on inc packets of flow                                                                                       |
| ipv6_src_addr                  | IPv6                  | IPv6 source address (disable)                                                                                                  |
| ipv6_dst_addr                  | IPv6                  | IPv6 destination address (disable)                                                                                             |
| ipv6_src_mask                  | UInt8                 | Length of IPv6 source mask in contiguous bits (disable)                                                                        |
| ipv6_dst_mask                  | UInt8                 | Length of IPv6 destination mask in contiguous bits (disable)                                                                   |
| ipv6_flow_label                | UInt32                | IPv6 flow label as in RFC2460 (disable)                                                                                        |
| icmp_type                      | UInt16                | ICMP packet type                                                                                                               |
| mul_igmp_type                  | UInt8                 | IGMP packet type                                                                                                               |
| sampling_interval              | UInt32                | Rate of sampling of packets                                                                                                    |
| sampling_algorithm             | UInt8                 | Type of algorithm for sampled netflow: 01 deterministic or 02 random sampling                                                  |
| flow_active_timeout            | UInt16                | Timeout value in seconds for active entries in netflow cache                                                                   |
| flow_inactive_timeout          | UInt16                | Timeout value in seconds for inactive entries in netflow cache                                                                 |
| engine_type                    | UInt8                 | Type of flow switching engine: RP|0, VIP/Linecard|1                                                                            |
| engine_id                      | UInt8                 | ID number of flow switching engine                                                                                             |
| total_bytes_exp                | UInt32                | Counter for bytes exported                                                                                                     |
| total_pkts_exp                 | UInt32                | Counter for pkts exported                                                                                                      |
| total_flows_exp                | UInt32                | Counter for flows exported                                                                                                     |
| ipv4_src_prefix                | UInt32                | IPv4 source address prefix Catalyst architecture                                                                               |
| ipv4_dst_prefix                | UInt32                | IPv4 destination address prefix Catalyst architecture                                                                          |
| mpls_top_label_type            | UInt8                 | MPLS top label type                                                                                                            |
| mpls_top_label_ip_addr         | UInt32                | Forwarding equivalent class corresponding to MPLS top label                                                                    |
| flow_sampler_id                | UInt8                 | ID from 'show flow-sampler'                                                                                                    |
| flow_sampler_mode              | UInt8                 | Type of algorithm used for sampling data                                                                                       |
| flow_sampler_random_interval   | UInt32                | Packet interval at which to sample                                                                                             |
| min_ttl                        | UInt8                 | Minimum TTL on incoming packets                                                                                                |
| max_ttl                        | UInt8                 | Maximum TTL on incoming packets                                                                                                |
| ipv4_ident                     | UInt16                | IPv4 identification field                                                                                                      |
| dst_tos                        | UInt8                 | Type of Service byte setting when exiting outgoing interface                                                                   |
| in_src_mac                     | UInt64                | Incoming source MAC address                                                                                                    |
| out_dst_mac                    | UInt64                | Outcoming destination MAC address                                                                                              |
| src_vlan                       | UInt16                | VLAN id associated with ingress interface                                                                                      |
| dst_vlan                       | UInt16                | VLAN id associated with egress interface                                                                                       |
| ip_protocol_version            | UInt8                 | IP protocol version for IPv4 is 4 and 6 for IPv6. If none, assumed 4                                                           |
| direction                      | UInt8                 | Flow direction: 0 -- ingress, 1 -- egress flow                                                                                 |
| ipv6_next_hop                  | IPv6                  | IPv6 address of nexthop router (disable)                                                                                       |
| bgp_ipv6_next_hop              | IPv6                  | IPv6 address of nexthop router in BGP domain (disable)                                                                         |
| ipv6_option_headers            | IPv6                  | Bit-encoded field identifying IPv6 option headers found in the flow (disable)                                                  |
| mpls_label1                    | UInt32                | MPLS label at position 1 in the stack. This comprises 20 bits of MPLS label, 3 EXP experimental bits and 1 S end-of-stack bit  |
| mpls_label2                    | UInt32                | MPLS label at position 2 in the stack. This comprises 20 bits of MPLS label, 3 EXP experimental bits and 1 S end-of-stack bit  |
| mpls_label3                    | UInt32                | MPLS label at position 3 in the stack. This comprises 20 bits of MPLS label, 3 EXP experimental bits and 1 S end-of-stack bit  |
| mpls_label4                    | UInt32                | MPLS label at position 4 in the stack. This comprises 20 bits of MPLS label, 3 EXP experimental bits and 1 S end-of-stack bit  |
| mpls_label5                    | UInt32                | MPLS label at position 5 in the stack. This comprises 20 bits of MPLS label, 3 EXP experimental bits and 1 S end-of-stack bit  |
| mpls_label6                    | UInt32                | MPLS label at position 6 in the stack. This comprises 20 bits of MPLS label, 3 EXP experimental bits and 1 S end-of-stack bit  |
| mpls_label7                    | UInt32                | MPLS label at position 7 in the stack. This comprises 20 bits of MPLS label, 3 EXP experimental bits and 1 S end-of-stack bit  |
| mpls_label8                    | UInt32                | MPLS label at position 8 in the stack. This comprises 20 bits of MPLS label, 3 EXP experimental bits and 1 S end-of-stack bit  |
| mpls_label9                    | UInt32                | MPLS label at position 9 in the stack. This comprises 20 bits of MPLS label, 3 EXP experimental bits and 1 S end-of-stack bit  |
| mpls_label10                   | UInt32                | MPLS label at position 10 in the stack. This comprises 20 bits of MPLS label, 3 EXP experimental bits and 1 S end-of-stack bit |
| in_dst_mac                     | UInt64                | Incoming destination MAC address                                                                                               |
| out_src_mac                    | UInt64                | Outcoming source MAC address                                                                                                   |
| if_name                        | String                | Shortened interface name i.e.: 'FE1/0'                                                                                         |
| if_desc                        | String                | Full interface name i.e.: 'FastEthernet 1/0'                                                                                   |
| sampler_name                   | String                | Name of the flow sampler                                                                                                       |
| in_permanent_bytes             | UInt32                | Running byte counter for a permanent flow                                                                                      |
| in_permanent_pkts              | UInt32                | Running packet counter for a permanent flow                                                                                    |
| fragment_offset                | UInt16                | The fragment-offset value from fragmented IP packets                                                                           |
| forwarding_status              | UInt8                 | Forwarding status is encoded on 1 byte with the 2 left bits giving the status and the 6 remaining bits giving the reason code. |
| mpls_pal_rd                    | UInt64                | MPLS PAL Route Distinguisher                                                                                                   |
| mpls_prefix_len                | UInt8                 | Number of consecutive bits in the MPLS prefix length                                                                           |
| src_traffic_index              | UInt32                | BGP Policy Accounting Source Traffic Index                                                                                     |
| dst_traffic_index              | UInt32                | BGP Policy Accounting Destination Traffic Index                                                                                |
| application_description        | String                | Application description                                                                                                        |
| application_tag                | UInt16                | 8 bits of engine ID, followed by n bits of classification                                                                      |
| application_name               | String                | Name associated with a classification                                                                                          |
| postipDiffServCodePoint        | UInt8                 | The value of a Differentiated Services Code Point DSCP encoded in the Differentiated Services Field, after modification        |
| replication_factor             | UInt32                | Multicast replication factor                                                                                                   |
