# Network


## Network | BFD | Session Down




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| interface | BFD interface |  |
| peer | BFD Peer |  |
| description | Interface description |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| BFD \| Session Down](../event-classes-reference/network.md#network-bfd-session-down) | :material-arrow-up: opening event |
| [Network \| BFD \| Session Up](../event-classes-reference/network.md#network-bfd-session-up) | :material-arrow-down: closing event |



## Network | BGP | Peer Down




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| peer | BGP Peer |  |
| vrf | VRF |  |
| reason | Reason |  |
| as | BGP Peer AS |  |
| local_as | Local AS |  |
| description | BGP Peer Description |  |
| import_filter | BGP Import Filter |  |
| export_filter | BGP Export Filter |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| BGP \| Backward Transition](../event-classes-reference/network.md#network-bgp-backward-transition) | :material-arrow-up: opening event |
| [Network \| BGP \| Established](../event-classes-reference/network.md#network-bgp-established) | :material-arrow-down: closing event |
| [Network \| BGP \| Peer Down](../event-classes-reference/network.md#network-bgp-peer-down) | :material-arrow-up: opening event |
| [Network \| BGP \| Peer State Changed](../event-classes-reference/network.md#network-bgp-peer-state-changed) | :material-arrow-up: opening event |
| [Network \| BGP \| Peer State Changed](../event-classes-reference/network.md#network-bgp-peer-state-changed) | :material-arrow-down: closing event |



## Network | BGP | Prefix Limit Exceeded




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| peer | BGP Peer |  |
| vrf | VRF |  |
| as | BGP Peer AS |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| BGP \| Established](../event-classes-reference/network.md#network-bgp-established) | :material-arrow-down: closing event |
| [Network \| BGP \| Peer State Changed](../event-classes-reference/network.md#network-bgp-peer-state-changed) | :material-arrow-down: closing event |
| [Network \| BGP \| Prefix Limit Exceeded](../event-classes-reference/network.md#network-bgp-prefix-limit-exceeded) | :material-arrow-up: opening event |



## Network | CEF | Resource Failure




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| peer | BFD Peer |  |
| reason | Reason failed |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| CEF \| Resource Failure](../event-classes-reference/network.md#network-cef-resource-failure) | :material-arrow-up: opening event |



## Network | DHCP | Untrusted Server




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| ip | Source IP |  |
| interface | Source interface |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| DHCP \| Untrusted Server](../event-classes-reference/network.md#network-dhcp-untrusted-server) | :material-arrow-up: opening event |



## Network | DNS | Bad Query




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| ip | Source IP |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| DNS \| Bad Query](../event-classes-reference/network.md#network-dns-bad-query) | :material-arrow-up: opening event |



## Network | DOCSIS | BPI Unautorized


<h3>Probable Causes</h3>
An unauthorized cable modem has been deleted to enforce BPI authorization for the specified cable modem. The specified cable modem was not performing BPI negotiation.


<h3>Recommended Actions</h3>
Check the modem interface configuration for privacy mandatory, or check for errors in the TFTP configuration file.


<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| mac | Cable Modem MAC |  |
| sid | Cable Modem SID |  |
| interface | Cable interface |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| DOCSIS \| BPI Unautorized](../event-classes-reference/network.md#network-docsis-bpi-unautorized) | :material-arrow-up: opening event |



## Network | DOCSIS | Bad Timing Offset


<h3>Probable Causes</h3>
The cable modem is not using the correct starting offset during initial ranging, causing a zero, negative timing offset to be recorded by the CMTS for this modem. The CMTS internal algorithms that rely on the timing offset parameter will not analyze any modems that do not use the correct starting offset. The modems may not be able to function, depending on their physical location on the cable plant.


<h3>Recommended Actions</h3>
Locate the cable modem based on the MAC address and report the initial timing offset problem to the cable modem vendor.


<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| mac | Cable Modem MAC |  |
| sid | Cable Modem SID |  |
| offset | Time offset |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| DOCSIS \| Bad Timing Offset](../event-classes-reference/network.md#network-docsis-bad-timing-offset) | :material-arrow-up: opening event |



## Network | DOCSIS | Invalid CoS


<h3>Probable Causes</h3>
The registration of the specified modem has failed because of an invalid or unsupported CoS setting.


<h3>Recommended Actions</h3>
Ensure that the CoS fields in the configuration file are set correctly.


<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| mac | Cable Modem MAC |  |
| sid | Cable Modem SID |  |
| interface | Cable interface |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| DOCSIS \| Invalid CoS](../event-classes-reference/network.md#network-docsis-invalid-cos) | :material-arrow-up: opening event |



## Network | DOCSIS | Invalid DOCSIS Message


<h3>Probable Causes</h3>
A cable modem that is not DOCSIS-compliant has attempted to send an invalid DOCSIS message.


<h3>Recommended Actions</h3>
Locate the cable modem that sent this message and replace it with DOCSIS-compliant modem.


<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| interface | Cable interface |  |
| mac | Cable Modem MAC |  |
| sid | Cable Modem SID |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| DOCSIS \| Invalid DOCSIS Message](../event-classes-reference/network.md#network-docsis-invalid-docsis-message) | :material-arrow-up: opening event |



## Network | DOCSIS | Invalid QoS


<h3>Probable Causes</h3>
The registration of the specified modem has failed because of an invalid or unsupported QoS setting.


<h3>Recommended Actions</h3>
Ensure that the QoS fields in the configuration file are set correctly.


<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| mac | Cable Modem MAC |  |
| sid | Cable Modem SID |  |
| interface | Cable interface |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| DOCSIS \| Invalid QoS](../event-classes-reference/network.md#network-docsis-invalid-qos) | :material-arrow-up: opening event |



## Network | DOCSIS | Invalid Shared Secret


<h3>Probable Causes</h3>
The registration of this modem has failed because of an invalid MIC string.


<h3>Recommended Actions</h3>
Ensure that the shared secret that is in the configuration file is the same as the shared secret that is configured in the cable modem.


<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| mac | Cable Modem MAC |  |
| sid | Cable Modem SID |  |
| interface | Cable interface |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| DOCSIS \| Invalid Shared Secret](../event-classes-reference/network.md#network-docsis-invalid-shared-secret) | :material-arrow-up: opening event |



## Network | DOCSIS | Max CPE Reached


<h3>Probable Causes</h3>
The maximum number of devices that can be attached to the cable modem has been exceeded. Therefore, the device with the specified IP address will not be added to the modem with the specified SID.


<h3>Recommended Actions</h3>
Locate the specified device and place the device on a different cable modem with another SID.


<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| mac | CPE MAC |  |
| ip | CPE IP |  |
| modem_mac | Cable Modem MAC |  |
| sid | Cable Modem SID |  |
| interface | Cable interface |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| DOCSIS \| Max CPE Reached](../event-classes-reference/network.md#network-docsis-max-cpe-reached) | :material-arrow-up: opening event |



## Network | DOCSIS | Maximum Capacity Reached


<h3>Probable Causes</h3>
The currently reserved capacity on the upstream channel already exceeds its virtual reservation capacity, based on the configured subscription level limit. Increasing the subscription level limit on the current upstream channel will place you at risk of being unable to guarantee the individual reserved rates for modems since this upstream channel is already oversubscribed.


<h3>Recommended Actions</h3>
Load-balance the modems that are requesting the reserved upstream rate on another upstream channel.


<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| interface | Cable interface |  |
| upstream | Upstream |  |
| cur_bps | Current bps reservation |  |
| res_bps | Reserved bps |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| DOCSIS \| Maximum Capacity Reached](../event-classes-reference/network.md#network-docsis-maximum-capacity-reached) | :material-arrow-up: opening event |



## Network | DOCSIS | Maximum SIDs


<h3>Probable Causes</h3>
The maximum number of SIDs has been allocated to the specified line card.


<h3>Recommended Actions</h3>
Assign the cable modem to another line card.


<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| interface | Cable interface |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| DOCSIS \| Maximum SIDs](../event-classes-reference/network.md#network-docsis-maximum-sids) | :material-arrow-up: opening event |



## Network | EIGRP | Neighbor Down

<h3>Symptoms</h3>
Routing table changes and possible lost of connectivity


<h3>Probable Causes</h3>
Link failure or protocol misconfiguration


<h3>Recommended Actions</h3>
Check links and local and neighbor router configuration


<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| as | EIGRP autonomus system |  |
| interface | Interface |  |
| neighbor | Neighbor's Router ID |  |
| reason | Adjacency lost reason |  |
| description | Interface description |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| EIGRP \| Neighbor Down](../event-classes-reference/network.md#network-eigrp-neighbor-down) | :material-arrow-up: opening event |
| [Network \| EIGRP \| Neighbor Up](../event-classes-reference/network.md#network-eigrp-neighbor-up) | :material-arrow-down: closing event |



## Network | IMPB | Unauthenticated IP-MAC

<h3>Symptoms</h3>
Discard user connection attempts



<h3>Recommended Actions</h3>
Check user IP and MAC, check IMPB entry, check topology


<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| ip | User IP |  |
| mac | User MAC |  |
| interface | Affected interface |  |
| description | Interface description |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| IMPB \| Recover IMPB stop learning state](../event-classes-reference/network.md#network-impb-recover-impb-stop-learning-state) | :material-arrow-down: closing event |
| [Network \| IMPB \| Unauthenticated IP-MAC](../event-classes-reference/network.md#network-impb-unauthenticated-ip-mac) | :material-arrow-up: opening event |



## Network | IP | ARP Moved




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| interface | BFD interface |  |
| ip | IP |  |
| from_mac | From MAC |  |
| to_mac | To MAC |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| IP \| ARP Moved](../event-classes-reference/network.md#network-ip-arp-moved) | :material-arrow-up: opening event |



## Network | IP | Address Conflict




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| ip | Conflicting IP |  |
| mac | MAC |  |
| interface | Interface |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| IP \| Address Conflict](../event-classes-reference/network.md#network-ip-address-conflict) | :material-arrow-up: opening event |



## Network | IP | IP Flap




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| ip | Flapped IP |  |
| from_interface | From interface |  |
| to_interface | To interface |  |
| mac | MAC |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| IP \| IP Flap](../event-classes-reference/network.md#network-ip-ip-flap) | :material-arrow-up: opening event |



## Network | IS-IS | Adjacency Down

<h3>Symptoms</h3>
Routing table changes and possible lost of connectivity


<h3>Probable Causes</h3>
Link failure or protocol misconfiguration


<h3>Recommended Actions</h3>
Check links and local and neighbor router configuration


<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| interface | Interface |  |
| neighbor | Neighbor's NSAP or name |  |
| level | Level |  |
| reason | Adjacency lost reason |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| IS-IS \| Adjacency Down](../event-classes-reference/network.md#network-is-is-adjacency-down) | :material-arrow-up: opening event |
| [Network \| IS-IS \| Adjacency Up](../event-classes-reference/network.md#network-is-is-adjacency-up) | :material-arrow-down: closing event |



## Network | LBD | Loop Detected



<h3>Recommended Actions</h3>
Check hardware link and topology


<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| interface | interface |  |
| description | Interface description |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| LBD \| Loop Cleared](../event-classes-reference/network.md#network-lbd-loop-cleared) | :material-arrow-down: closing event |
| [Network \| LBD \| Loop Detected](../event-classes-reference/network.md#network-lbd-loop-detected) | :material-arrow-up: opening event |



## Network | LBD | Vlan Loop Detected

<h3>Symptoms</h3>
Lost traffic on specific vlan



<h3>Recommended Actions</h3>
Check topology or use STP to avoid loops


<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| interface | interface |  |
| vlan | Vlan |  |
| description | Interface description |  |
| vlan_name | Vlan name |  |
| vlan_description | Vlan description |  |
| vlan_l2_domain | L2 domain |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| LBD \| Vlan Loop Cleared](../event-classes-reference/network.md#network-lbd-vlan-loop-cleared) | :material-arrow-down: closing event |
| [Network \| LBD \| Vlan Loop Detected](../event-classes-reference/network.md#network-lbd-vlan-loop-detected) | :material-arrow-up: opening event |



## Network | Link | DOM | Alarm: Out of Threshold

<h3>Symptoms</h3>
Connection lost




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| interface | Physical port |  |
| threshold | Threshold type |  |
| sensor | Measured name |  |
| ovalue | Operating value |  |
| tvalue | Threshold value |  |
| description | Interface description |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| Link \| DOM \| Alarm: Out of Threshold](../event-classes-reference/network.md#network-link-dom-alarm:-out-of-threshold) | :material-arrow-up: opening event |
| [Network \| Link \| DOM \| Alarm: Out of Threshold Recovered](../event-classes-reference/network.md#network-link-dom-alarm:-out-of-threshold-recovered) | :material-arrow-down: closing event |



## Network | Link | DOM | Warning: Out of Threshold

<h3>Symptoms</h3>
Connection lost




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| interface | Physical port |  |
| threshold | Threshold type |  |
| sensor | Measured name |  |
| ovalue | Operating value |  |
| tvalue | Threshold value |  |
| description | Interface description |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| Link \| DOM \| Warning: Out of Threshold](../event-classes-reference/network.md#network-link-dom-warning:-out-of-threshold) | :material-arrow-up: opening event |
| [Network \| Link \| DOM \| Warning: Out of Threshold Recovered](../event-classes-reference/network.md#network-link-dom-warning:-out-of-threshold-recovered) | :material-arrow-down: closing event |



## Network | Link | Duplex Mismatch




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| interface | interface name |  |
| description | Interface description |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| Link \| Duplex Mismatch](../event-classes-reference/network.md#network-link-duplex-mismatch) | :material-arrow-up: opening event |



## Network | Link | Err-Disable




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| interface | interface name |  |
| reason | err-disable reason |  |
| description | Interface description |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| Link \| Err-Disable](../event-classes-reference/network.md#network-link-err-disable) | :material-arrow-up: opening event |
| [Network \| Link \| Link Flap Error Detected](../event-classes-reference/network.md#network-link-link-flap-error-detected) | :material-arrow-up: opening event |
| [Network \| Link \| Link Flap Error Recovery](../event-classes-reference/network.md#network-link-link-flap-error-recovery) | :material-arrow-down: closing event |
| [Network \| Link \| Link Up](../event-classes-reference/network.md#network-link-link-up) | :material-arrow-down: closing event |



## Network | Link | Half-Duplex




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| interface | interface name |  |
| description | Interface description |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| Link \| Full-Duplex](../event-classes-reference/network.md#network-link-full-duplex) | :material-arrow-down: closing event |
| [Network \| Link \| Half-Duplex](../event-classes-reference/network.md#network-link-half-duplex) | :material-arrow-up: opening event |



## Network | Link | Link Down

<h3>Symptoms</h3>
Connection lost


<h3>Probable Causes</h3>
Administrative action, cable damage, hardware or software error either from this or from another side


<h3>Recommended Actions</h3>
Check configuration, both sides of links and hardware


<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| interface | interface name |  |
| description | Interface description |  |
| link | Link ID |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| Link \| Link Down](../event-classes-reference/network.md#network-link-link-down) | :material-arrow-up: opening event |
| [Network \| Link \| Link Up](../event-classes-reference/network.md#network-link-link-up) | :material-arrow-down: closing event |



## Network | MAC | Duplicate MAC




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| mac | MAC Address |  |
| one_interface | First interface |  |
| two_interface | Second interface |  |
| one_description | Interface description |  |
| two_description | Interface description |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| MAC \| Duplicate MAC](../event-classes-reference/network.md#network-mac-duplicate-mac) | :material-arrow-up: opening event |



## Network | MAC | Invalid MAC




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| mac | MAC Address |  |
| interface | Affected interface |  |
| vlan | Affected vlan |  |
| description | Interface description |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| MAC \| Invalid MAC](../event-classes-reference/network.md#network-mac-invalid-mac) | :material-arrow-up: opening event |



## Network | MAC | Link MAC Exceed




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| mac_limit | MAC Address Limit |  |
| utilization | Utilization |  |
| interface | Interface |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| MAC \| Link MAC Exceed](../event-classes-reference/network.md#network-mac-link-mac-exceed) | :material-arrow-up: opening event |



## Network | MAC | MAC Flap


<h3>Probable Causes</h3>
The system found the specified host moving between the specified ports.


<h3>Recommended Actions</h3>
Examine the network for possible loops.


<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| mac | MAC Address |  |
| vlan | VLAN |  |
| from_interface | From interface |  |
| to_interface | To interface |  |
| from_description | Interface description |  |
| to_description | Interface description |  |
| vlan_name | Vlan name |  |
| vlan_description | Vlan description |  |
| vlan_l2_domain | L2 domain |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| MAC \| MAC Flap](../event-classes-reference/network.md#network-mac-mac-flap) | :material-arrow-up: opening event |



## Network | MAC | MAC Flood




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| mac | MAC Address |  |
| vlan | VLAN |  |
| interface | Interface |  |
| vlan_name | Vlan name |  |
| vlan_description | Vlan description |  |
| vlan_l2_domain | L2 domain |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| MAC \| MAC Flood](../event-classes-reference/network.md#network-mac-mac-flood) | :material-arrow-up: opening event |



## Network | MPLS | LDP Neighbor Down




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| neighbor | LDP Neighbor |  |
| state | State |  |
| reason | Reason |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| MPLS \| LDP Neighbor Down](../event-classes-reference/network.md#network-mpls-ldp-neighbor-down) | :material-arrow-up: opening event |
| [Network \| MPLS \| LDP Neighbor Up](../event-classes-reference/network.md#network-mpls-ldp-neighbor-up) | :material-arrow-down: closing event |



## Network | MPLS | LDP Session Down




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| interface | interface name |  |
| state | State |  |
| reason | Reason |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| MPLS \| LDP Session Down](../event-classes-reference/network.md#network-mpls-ldp-session-down) | :material-arrow-up: opening event |
| [Network \| MPLS \| LDP Session Up](../event-classes-reference/network.md#network-mpls-ldp-session-up) | :material-arrow-down: closing event |



## Network | MPLS | LSP Down




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| name | LSP name |  |
| state | State |  |
| reason | Reason |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| MPLS \| LSP Down](../event-classes-reference/network.md#network-mpls-lsp-down) | :material-arrow-up: opening event |
| [Network \| MPLS \| LSP Up](../event-classes-reference/network.md#network-mpls-lsp-up) | :material-arrow-down: closing event |



## Network | MPLS | Path Down




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| name | Path name |  |
| reason | Reason |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| MPLS \| Path Down](../event-classes-reference/network.md#network-mpls-path-down) | :material-arrow-up: opening event |
| [Network \| MPLS \| Path Up](../event-classes-reference/network.md#network-mpls-path-up) | :material-arrow-down: closing event |



## Network | MPLS | TDP Neighbor Down




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| neighbor | TDP Neighbor |  |
| reason | Reason |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| MPLS \| TDP Neighbor Down](../event-classes-reference/network.md#network-mpls-tdp-neighbor-down) | :material-arrow-up: opening event |
| [Network \| MPLS \| TDP Neighbor Up](../event-classes-reference/network.md#network-mpls-tdp-neighbor-up) | :material-arrow-down: closing event |



## Network | MSDP | Peer Down



<h3>Recommended Actions</h3>
Check msdp peer aviability, check msdp peer configuration changes


<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| peer | Peer's IP |  |
| vrf | VRF |  |
| reason | Reason |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| MSDP \| Peer Down](../event-classes-reference/network.md#network-msdp-peer-down) | :material-arrow-up: opening event |
| [Network \| MSDP \| Peer Up](../event-classes-reference/network.md#network-msdp-peer-up) | :material-arrow-down: closing event |



## Network | Monitor | CRC Error Detected




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| interface | interface |  |
| description | Interface description |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| Monitor \| CRC Error Cleared](../event-classes-reference/network.md#network-monitor-crc-error-cleared) | :material-arrow-down: closing event |
| [Network \| Monitor \| CRC Error Detected](../event-classes-reference/network.md#network-monitor-crc-error-detected) | :material-arrow-up: opening event |



## Network | OSPF | Neighbor Down

<h3>Symptoms</h3>
Routing table changes and possible lost of connectivity


<h3>Probable Causes</h3>
Link failure or protocol misconfiguration


<h3>Recommended Actions</h3>
Check links and local and neighbor router configuration


<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| area | OSPF area |  |
| interface | Interface |  |
| neighbor | Neighbor's Router ID |  |
| reason | Adjacency lost reason |  |
| vrf | VRF |  |
| description | Interface description |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| OSPF \| Neighbor Down](../event-classes-reference/network.md#network-ospf-neighbor-down) | :material-arrow-up: opening event |
| [Network \| OSPF \| Neighbor Up](../event-classes-reference/network.md#network-ospf-neighbor-up) | :material-arrow-down: closing event |



## Network | PIM | DR Change

<h3>Symptoms</h3>
Some multicast flows lost


<h3>Probable Causes</h3>
Link failure or protocol misconfiguration


<h3>Recommended Actions</h3>
Check links and local and neighbor router configuration


<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| interface | Interface |  |
| from_dr | From DR |  |
| to_dr | To DR |  |
| vrf | VRF |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| PIM \| DR Change](../event-classes-reference/network.md#network-pim-dr-change) | :material-arrow-up: opening event |



## Network | PIM | Invalid RP


<h3>Probable Causes</h3>
A PIM router received a register message from another PIM router that identifies itself as the rendezvous point. If the router is not configured for another rendezvous point, it will not accept the register message.


<h3>Recommended Actions</h3>
Configure all leaf routers (first-hop routers to multicast sources) with the IP address of the valid rendezvous point.


<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| pim_router | PIM router IP |  |
| invalid_rp | Invalid RP IP |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| PIM \| Invalid RP](../event-classes-reference/network.md#network-pim-invalid-rp) | :material-arrow-up: opening event |



## Network | PIM | MSDP Peer Down

<h3>Symptoms</h3>
Multicast flows lost


<h3>Probable Causes</h3>
Link failure or protocol misconfiguration


<h3>Recommended Actions</h3>
Check links and local and neighbor router configuration


<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| peer | Peer's IP |  |
| vrf | VRF |  |
| reason | Reason |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| PIM \| MSDP Peer Down](../event-classes-reference/network.md#network-pim-msdp-peer-down) | :material-arrow-up: opening event |
| [Network \| PIM \| MSDP Peer Up](../event-classes-reference/network.md#network-pim-msdp-peer-up) | :material-arrow-down: closing event |



## Network | PIM | Neighbor Down

<h3>Symptoms</h3>
Multicast flows lost


<h3>Probable Causes</h3>
Link failure or protocol misconfiguration


<h3>Recommended Actions</h3>
Check links and local and neighbor router configuration


<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| interface | Interface |  |
| neighbor | Neighbor's IP |  |
| vrf | VRF |  |
| reason | Reason |  |
| description | Interface description |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| PIM \| Neighbor Down](../event-classes-reference/network.md#network-pim-neighbor-down) | :material-arrow-up: opening event |
| [Network \| PIM \| Neighbor Up](../event-classes-reference/network.md#network-pim-neighbor-up) | :material-arrow-down: closing event |



## Network | Port Security | Port Security Violation




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| interface | Interface |  |
| mac | MAC Address |  |
| description | Interface description |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| Port Security \| Port Security Violation](../event-classes-reference/network.md#network-port-security-port-security-violation) | :material-arrow-up: opening event |



## Network | Port | Loss of Signal

<h3>Symptoms</h3>
Connection lost


<h3>Probable Causes</h3>
Administrative action, cable damage, hardware or software error either from this or from another side


<h3>Recommended Actions</h3>
Check configuration, both sides of links and hardware


<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| interface | interface name |  |
| description | Interface description |  |
| slot | Slot name |  |
| catrd | Card name |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| Port \| Loss of Signal](../event-classes-reference/network.md#network-port-loss-of-signal) | :material-arrow-up: opening event |
| [Network \| Port \| Loss of Signal Resume](../event-classes-reference/network.md#network-port-loss-of-signal-resume) | :material-arrow-down: closing event |



## Network | RSVP | Neighbor Down

<h3>Symptoms</h3>
Routing table changes and possible lost of connectivity


<h3>Probable Causes</h3>
Link failure or protocol misconfiguration


<h3>Recommended Actions</h3>
Check links and local and neighbor router configuration


<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| interface | Interface |  |
| neighbor | Neighbor's NSAP or name |  |
| reason | Neighbor lost reason |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| RSVP \| Neighbor Down](../event-classes-reference/network.md#network-rsvp-neighbor-down) | :material-arrow-up: opening event |
| [Network \| RSVP \| Neighbor Up](../event-classes-reference/network.md#network-rsvp-neighbor-up) | :material-arrow-down: closing event |



## Network | STP | BPDU Guard Violation




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| interface | interface |  |
| description | Interface description |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| Link \| Link Up](../event-classes-reference/network.md#network-link-link-up) | :material-arrow-down: closing event |
| [Network \| STP \| BPDU Guard Recovery](../event-classes-reference/network.md#network-stp-bpdu-guard-recovery) | :material-arrow-down: closing event |
| [Network \| STP \| BPDU Guard Violation](../event-classes-reference/network.md#network-stp-bpdu-guard-violation) | :material-arrow-up: opening event |



## Network | STP | Root Guard Violation




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| interface | interface |  |
| description | Interface description |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| Link \| Link Up](../event-classes-reference/network.md#network-link-link-up) | :material-arrow-down: closing event |
| [Network \| STP \| BPDU Root Violation](../event-classes-reference/network.md#network-stp-bpdu-root-violation) | :material-arrow-up: opening event |
| [Network \| STP \| Root Guard Recovery](../event-classes-reference/network.md#network-stp-root-guard-recovery) | :material-arrow-down: closing event |



## Network | STP | STP Loop Detected




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| interface | interface |  |
| description | Interface description |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| STP \| STP Loop Cleared](../event-classes-reference/network.md#network-stp-stp-loop-cleared) | :material-arrow-down: closing event |
| [Network \| STP \| STP Loop Detected](../event-classes-reference/network.md#network-stp-stp-loop-detected) | :material-arrow-up: opening event |



## Network | STP | STP Vlan Loop Detected




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| interface | interface |  |
| vlan | vlan |  |
| description | Interface description |  |
| vlan_name | Vlan name |  |
| vlan_description | Vlan description |  |
| vlan_l2_domain | L2 domain |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| STP \| STP Vlan Loop Cleared](../event-classes-reference/network.md#network-stp-stp-vlan-loop-cleared) | :material-arrow-down: closing event |
| [Network \| STP \| STP Vlan Loop Detected](../event-classes-reference/network.md#network-stp-stp-vlan-loop-detected) | :material-arrow-up: opening event |



## Network | Storm Control | Broadcast Storm Detected




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| interface | interface |  |
| description | Interface description |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| Storm Control \| Broadcast Storm Cleared](../event-classes-reference/network.md#network-storm-control-broadcast-storm-cleared) | :material-arrow-down: closing event |
| [Network \| Storm Control \| Broadcast Storm Detected](../event-classes-reference/network.md#network-storm-control-broadcast-storm-detected) | :material-arrow-up: opening event |



## Network | Storm Control | Multicast Storm Detected




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| interface | interface |  |
| description | Interface description |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| Storm Control \| Multicast Storm Cleared](../event-classes-reference/network.md#network-storm-control-multicast-storm-cleared) | :material-arrow-down: closing event |
| [Network \| Storm Control \| Multicast Storm Detected](../event-classes-reference/network.md#network-storm-control-multicast-storm-detected) | :material-arrow-up: opening event |



## Network | Storm Control | Storm Detected




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| interface | interface |  |
| description | Interface description |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| Storm Control \| Storm Cleared](../event-classes-reference/network.md#network-storm-control-storm-cleared) | :material-arrow-down: closing event |
| [Network \| Storm Control \| Storm Detected](../event-classes-reference/network.md#network-storm-control-storm-detected) | :material-arrow-up: opening event |



## Network | Storm Control | Unicast Storm Detected



<h3>Recommended Actions</h3>
Enable DLF (destination lookup failure) filter


<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| interface | interface |  |
| description | Interface description |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| Storm Control \| Unicast Storm Cleared](../event-classes-reference/network.md#network-storm-control-unicast-storm-cleared) | :material-arrow-down: closing event |
| [Network \| Storm Control \| Unicast Storm Detected](../event-classes-reference/network.md#network-storm-control-unicast-storm-detected) | :material-arrow-up: opening event |



## Network | UDLD | UDLD Protocol Error Detected




<h3>Variables</h3>
| Name | Description | Defaults |
| --- | --- | --- |
| interface | interface |  |
| description | Interface description |  |



<h3>Related Events</h3>
| Event Class | Role |
| --- | --- |
| [Network \| UDLD \| UDLD Protocol Error Detected](../event-classes-reference/network.md#network-udld-udld-protocol-error-detected) | :material-arrow-up: opening event |
| [Network \| UDLD \| UDLD Protocol Recovery](../event-classes-reference/network.md#network-udld-udld-protocol-recovery) | :material-arrow-down: closing event |


