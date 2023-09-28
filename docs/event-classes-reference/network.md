# Network | *


## Network | 802.11 | Associated




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Radio interface | {{ no }} |
| mac | `mac` | Station MAC | {{ no }} |




## Network | 802.11 | Disassociated




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Radio interface | {{ no }} |
| mac | `mac` | Station MAC | {{ no }} |
| reason | `str` | Reason | {{ no }} |




## Network | 802.11 | Max Retries




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| mac | `mac` | Station MAC | {{ no }} |




## Network | 802.11 | Roamed




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| mac | `mac` | Station MAC | {{ no }} |
| station | `mac` | Receiving station's MAC | {{ no }} |




## Network | BFD | Session Down




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | BFD interface | {{ yes }} |
| peer | `ip_address` | BFD Peer | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| BFD \| Session Down](../alarm-classes-reference/network.md#network-bfd-session-down) | :material-arrow-up: opening event | dispose |



## Network | BFD | Session Up




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | BFD interface | {{ yes }} |
| peer | `ip_address` | BFD Peer | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| BFD \| Session Down](../alarm-classes-reference/network.md#network-bfd-session-down) | :material-arrow-down: closing event | dispose |



## Network | BGP | Backward Transition




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| peer | `ip_address` | Peer | {{ yes }} |
| vrf | `str` | VRF | {{ no }} |
| as | `int` | Peer AS | {{ no }} |
| state | `str` | Transition from state | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| BGP \| Peer Down](../alarm-classes-reference/network.md#network-bgp-peer-down) | :material-arrow-up: opening event | dispose |



## Network | BGP | Established




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| peer | `ip_address` | Peer | {{ yes }} |
| vrf | `str` | VRF | {{ no }} |
| as | `int` | Peer AS | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| BGP \| Peer Down](../alarm-classes-reference/network.md#network-bgp-peer-down) | :material-arrow-down: closing event | dispose |
| [Network \| BGP \| Prefix Limit Exceeded](../alarm-classes-reference/network.md#network-bgp-prefix-limit-exceeded) | :material-arrow-down: closing event | dispose |



## Network | BGP | Max Prefixes Exceeds




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| peer | `ip_address` | Peer | {{ yes }} |
| vrf | `str` | VRF | {{ no }} |
| as | `int` | Peer AS | {{ no }} |
| recv | `int` | Prefixes recieved | {{ yes }} |
| max | `int` | Maximum prefixes | {{ no }} |




## Network | BGP | Max Prefixes Warning




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| peer | `ip_address` | Peer | {{ yes }} |
| vrf | `str` | VRF | {{ no }} |
| as | `int` | Peer AS | {{ no }} |
| recv | `int` | Prefixes recieved | {{ yes }} |
| max | `int` | Maximum prefixes | {{ no }} |




## Network | BGP | Peer Down




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| peer | `ip_address` | Peer | {{ yes }} |
| vrf | `str` | VRF | {{ no }} |
| as | `int` | Peer AS | {{ no }} |
| reason | `str` | Reason | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| BGP \| Peer Down](../alarm-classes-reference/network.md#network-bgp-peer-down) | :material-arrow-up: opening event | dispose |



## Network | BGP | Peer State Changed




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| peer | `ip_address` | Peer | {{ yes }} |
| vrf | `str` | VRF | {{ no }} |
| as | `int` | Peer AS | {{ no }} |
| from_state | `str` | Initial state | {{ no }} |
| to_state | `str` | Final state | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| BGP \| Peer Down](../alarm-classes-reference/network.md#network-bgp-peer-down) | :material-arrow-up: opening event | raise |
| [Network \| BGP \| Peer Down](../alarm-classes-reference/network.md#network-bgp-peer-down) | :material-arrow-down: closing event | clear_peer_down |
| [Network \| BGP \| Prefix Limit Exceeded](../alarm-classes-reference/network.md#network-bgp-prefix-limit-exceeded) | :material-arrow-down: closing event | clear_maxprefix |



## Network | BGP | Prefix Limit Exceeded




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| peer | `ip_address` | Peer | {{ yes }} |
| vrf | `str` | VRF | {{ no }} |
| as | `int` | Peer AS | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| BGP \| Prefix Limit Exceeded](../alarm-classes-reference/network.md#network-bgp-prefix-limit-exceeded) | :material-arrow-up: opening event | dispose |



## Network | CEF | Inconsistency Detection




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| time | `int` | sysUpTime | {{ no }} |




## Network | CEF | Peer State Changed




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| peer | `ip_address` | Peer | {{ yes }} |
| state | `str` | Peer state | {{ no }} |




## Network | CEF | Resource Failure




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| peer | `ip_address` | Peer | {{ yes }} |
| reason | `str` | Reason failed | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| CEF \| Resource Failure](../alarm-classes-reference/network.md#network-cef-resource-failure) | :material-arrow-up: opening event | dispose |



## Network | DHCP | Untrusted Server




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| ip | `ip_address` | Source IP | {{ yes }} |
| interface | `interface_name` | Source interface | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| DHCP \| Untrusted Server](../alarm-classes-reference/network.md#network-dhcp-untrusted-server) | :material-arrow-up: opening event | dispose |



## Network | DNS | Bad Query




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| ip | `ip_address` | Source IP | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| DNS \| Bad Query](../alarm-classes-reference/network.md#network-dns-bad-query) | :material-arrow-up: opening event | dispose |



## Network | DOCSIS | BPI Unautorized


<h3>Probable Causes</h3>
An unauthorized cable modem has been deleted to enforce BPI authorization for the specified cable modem. The specified cable modem was not performing BPI negotiation.


<h3>Recommended Actions</h3>
Check the modem interface configuration for privacy mandatory, or check for errors in the TFTP configuration file.


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| mac | `mac` | Cable Modem MAC | {{ yes }} |
| sid | `int` | Cable Modem SID | {{ no }} |
| interface | `interface_name` | Cable interface | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| DOCSIS \| BPI Unautorized](../alarm-classes-reference/network.md#network-docsis-bpi-unautorized) | :material-arrow-up: opening event | dispose |



## Network | DOCSIS | Bad Timing Offset


<h3>Probable Causes</h3>
The cable modem is not using the correct starting offset during initial ranging, causing a zero, negative timing offset to be recorded by the CMTS for this modem. The CMTS internal algorithms that rely on the timing offset parameter will not analyze any modems that do not use the correct starting offset. The modems may not be able to function, depending on their physical location on the cable plant.


<h3>Recommended Actions</h3>
Locate the cable modem based on the MAC address and report the initial timing offset problem to the cable modem vendor.


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| mac | `mac` | Cable Modem MAC | {{ no }} |
| sid | `int` | Cable Modem SID | {{ no }} |
| offset | `str` | Time offset | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| DOCSIS \| Bad Timing Offset](../alarm-classes-reference/network.md#network-docsis-bad-timing-offset) | :material-arrow-up: opening event | dispose |



## Network | DOCSIS | Channel Width Changed


<h3>Probable Causes</h3>
The upstream channel frequency has been changed.



<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Cable interface | {{ yes }} |
| upstream | `str` | Upstream | {{ no }} |
| width | `str` | Channel width | {{ yes }} |




## Network | DOCSIS | Invalid CoS


<h3>Probable Causes</h3>
The registration of the specified modem has failed because of an invalid or unsupported CoS setting.


<h3>Recommended Actions</h3>
Ensure that the CoS fields in the configuration file are set correctly.


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| mac | `mac` | Cable Modem MAC | {{ yes }} |
| sid | `int` | Cable Modem SID | {{ no }} |
| interface | `interface_name` | Cable interface | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| DOCSIS \| Invalid CoS](../alarm-classes-reference/network.md#network-docsis-invalid-cos) | :material-arrow-up: opening event | dispose |



## Network | DOCSIS | Invalid DOCSIS Message


<h3>Probable Causes</h3>
A cable modem that is not DOCSIS-compliant has attempted to send an invalid DOCSIS message.


<h3>Recommended Actions</h3>
Locate the cable modem that sent this message and replace it with DOCSIS-compliant modem.


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Cable interface | {{ no }} |
| mac | `mac` | Cable Modem MAC | {{ no }} |
| sid | `int` | Cable Modem SID | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| DOCSIS \| Invalid DOCSIS Message](../alarm-classes-reference/network.md#network-docsis-invalid-docsis-message) | :material-arrow-up: opening event | dispose |



## Network | DOCSIS | Invalid QoS


<h3>Probable Causes</h3>
The registration of the specified modem has failed because of an invalid or unsupported QoS setting.


<h3>Recommended Actions</h3>
Ensure that the QoS fields in the configuration file are set correctly.


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| mac | `mac` | Cable Modem MAC | {{ yes }} |
| sid | `int` | Cable Modem SID | {{ no }} |
| interface | `interface_name` | Cable interface | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| DOCSIS \| Invalid QoS](../alarm-classes-reference/network.md#network-docsis-invalid-qos) | :material-arrow-up: opening event | dispose |



## Network | DOCSIS | Invalid Shared Secret


<h3>Probable Causes</h3>
The registration of this modem has failed because of an invalid MIC string.


<h3>Recommended Actions</h3>
Ensure that the shared secret that is in the configuration file is the same as the shared secret that is configured in the cable modem.


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| mac | `mac` | Cable Modem MAC | {{ yes }} |
| sid | `int` | Cable Modem SID | {{ no }} |
| interface | `interface_name` | Cable interface | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| DOCSIS \| Invalid Shared Secret](../alarm-classes-reference/network.md#network-docsis-invalid-shared-secret) | :material-arrow-up: opening event | dispose |



## Network | DOCSIS | Max CPE Reached


<h3>Probable Causes</h3>
The maximum number of devices that can be attached to the cable modem has been exceeded. Therefore, the device with the specified IP address will not be added to the modem with the specified SID.


<h3>Recommended Actions</h3>
Locate the specified device and place the device on a different cable modem with another SID.


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| mac | `mac` | CPE MAC | {{ no }} |
| ip | `ip_address` | CPE IP | {{ no }} |
| modem_mac | `mac` | Cable Modem MAC | {{ no }} |
| sid | `int` | Cable Modem SID | {{ no }} |
| interface | `interface_name` | Cable interface | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| DOCSIS \| Max CPE Reached](../alarm-classes-reference/network.md#network-docsis-max-cpe-reached) | :material-arrow-up: opening event | dispose |



## Network | DOCSIS | Maximum Capacity Reached


<h3>Probable Causes</h3>
The currently reserved capacity on the upstream channel already exceeds its virtual reservation capacity, based on the configured subscription level limit. Increasing the subscription level limit on the current upstream channel will place you at risk of being unable to guarantee the individual reserved rates for modems since this upstream channel is already oversubscribed.


<h3>Recommended Actions</h3>
Load-balance the modems that are requesting the reserved upstream rate on another upstream channel.


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Cable interface | {{ yes }} |
| upstream | `str` | Upstream | {{ no }} |
| cur_bps | `int` | Current bps reservation | {{ no }} |
| res_bps | `int` | Reserved bps | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| DOCSIS \| Maximum Capacity Reached](../alarm-classes-reference/network.md#network-docsis-maximum-capacity-reached) | :material-arrow-up: opening event | dispose |



## Network | DOCSIS | Maximum SIDs


<h3>Probable Causes</h3>
The maximum number of SIDs has been allocated to the specified line card.


<h3>Recommended Actions</h3>
Assign the cable modem to another line card.


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Cable interface | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| DOCSIS \| Maximum SIDs](../alarm-classes-reference/network.md#network-docsis-maximum-sids) | :material-arrow-up: opening event | dispose |



## Network | DOCSIS | Unregistered Modem Deleted


<h3>Probable Causes</h3>
An unregistered cable modem has been deleted to avoid unaccounted bandwidth usage.


<h3>Recommended Actions</h3>
Check the cable modem interface configuration for registration bypass, or check for errors in the TFTP configuration file. 


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| mac | `mac` | Cable Modem MAC | {{ yes }} |




## Network | DOCSIS | Upstream Frequency Changed


<h3>Probable Causes</h3>
The upstream channel frequency has been changed.



<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Cable interface | {{ yes }} |
| upstream | `str` | Upstream | {{ no }} |
| frequency | `str` | Frequency | {{ yes }} |




## Network | DOCSIS | Upstream Input Power Level Changed


<h3>Probable Causes</h3>
The upstream channel input power level has been changed.



<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Cable interface | {{ yes }} |
| upstream | `str` | Upstream | {{ no }} |
| power | `int` | Input power | {{ yes }} |




## Network | EIGRP | Neighbor Down
<h3>Symptoms</h3>
Routing table changes and possible lost of connectivity


<h3>Probable Causes</h3>
Link failure or protocol misconfiguration


<h3>Recommended Actions</h3>
Check links and local and neighbor router configuration


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| as | `str` | EIGRP automonus system | {{ no }} |
| interface | `str` | Interface | {{ yes }} |
| neighbor | `ip_address` | Neighbor's Router ID | {{ yes }} |
| reason | `str` | Adjacency lost reason | {{ no }} |
| to_state | `str` | to state | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| EIGRP \| Neighbor Down](../alarm-classes-reference/network.md#network-eigrp-neighbor-down) | :material-arrow-up: opening event | dispose |



## Network | EIGRP | Neighbor Up
<h3>Symptoms</h3>
Routing table changes


<h3>Probable Causes</h3>
An EIGRP adjacency was established with the indicated neighboring router. The local router can now exchange information with it.


<h3>Recommended Actions</h3>
No specific actions needed


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| as | `str` | EIGRP autonomus system | {{ no }} |
| interface | `str` | Interface | {{ yes }} |
| neighbor | `ip_address` | Neighbor's Router ID | {{ yes }} |
| reason | `str` | Adjacency lost reason | {{ no }} |
| to_state | `str` | to state | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| EIGRP \| Neighbor Down](../alarm-classes-reference/network.md#network-eigrp-neighbor-down) | :material-arrow-down: closing event | dispose |



## Network | HSRP | GRP State Changed




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| group | `str` | Group | {{ yes }} |
| interface | `interface_name` | Affected interface | {{ yes }} |
| state | `str` | HSRP state | {{ no }} |




## Network | IMPB | Dynamic IMPB entry is conflicting with static
<h3>Symptoms</h3>
Discard user connection attemps



<h3>Recommended Actions</h3>
Check user IP and MAC, check DHCP database


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| ip | `ip_address` | User IP | {{ yes }} |
| mac | `mac` | User MAC | {{ yes }} |
| interface | `interface_name` | Affected interface | {{ yes }} |




## Network | IMPB | Recover IMPB stop learning state
<h3>Symptoms</h3>
Restore ability for incoming connections



<h3>Recommended Actions</h3>
Check IMPB entry, check topology


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Affected interface | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| IMPB \| Unauthenticated IP-MAC](../alarm-classes-reference/network.md#network-impb-unauthenticated-ip-mac) | :material-arrow-down: closing event | dispose |



## Network | IMPB | Unauthenticated IP-MAC
<h3>Symptoms</h3>
Discard user connection attempts



<h3>Recommended Actions</h3>
Check user IP and MAC, check IMPB entry, check topology


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| ip | `ip_address` | User IP | {{ yes }} |
| mac | `mac` | User MAC | {{ yes }} |
| interface | `interface_name` | Affected interface | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| IMPB \| Unauthenticated IP-MAC](../alarm-classes-reference/network.md#network-impb-unauthenticated-ip-mac) | :material-arrow-up: opening event | dispose |



## Network | IP | ARP Moved




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | BFD interface | {{ no }} |
| ip | `ip_address` | IP | {{ yes }} |
| from_mac | `mac` | From MAC | {{ yes }} |
| to_mac | `mac` | To MAC | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| IP \| ARP Moved](../alarm-classes-reference/network.md#network-ip-arp-moved) | :material-arrow-up: opening event | dispose |



## Network | IP | ARP Zero MAC




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| ip | `ip_address` | IP | {{ yes }} |
| interface | `interface_name` | Affected interface | {{ no }} |




## Network | IP | Address Conflict




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| ip | `ip_address` | Conflicting IP | {{ yes }} |
| mac | `mac` | MAC | {{ no }} |
| interface | `interface_name` | Interface | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| IP \| Address Conflict](../alarm-classes-reference/network.md#network-ip-address-conflict) | :material-arrow-up: opening event | dispose |



## Network | IP | IP Flap




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| ip | `ip_address` | Flapped IP | {{ yes }} |
| mac | `mac` | MAC | {{ no }} |
| from_interface | `interface_name` | From interface | {{ yes }} |
| to_interface | `interface_name` | To interface | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| IP \| IP Flap](../alarm-classes-reference/network.md#network-ip-ip-flap) | :material-arrow-up: opening event | dispose |



## Network | IP | Port Exhaustion
<h3>Symptoms</h3>
Failed to establish outgoung connection


<h3>Probable Causes</h3>
No free TCP/UDP ports for outgoung connection


<h3>Recommended Actions</h3>
Check applications and aging intervals


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| src_ip | `ip_address` | Source address | {{ no }} |
| dst_ip | `ip_address` | Destination address | {{ no }} |
| dst_port | `int` | Destination port | {{ no }} |
| proto | `int` | Protocol | {{ no }} |




## Network | IP | Route Limit Exceeded




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| reason | `str` | Reason | {{ no }} |




## Network | IP | Route Limit Warning




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| reason | `str` | Reason | {{ no }} |




## Network | IS-IS | Adjacency Down
<h3>Symptoms</h3>
Routing table changes and possible lost of connectivity


<h3>Probable Causes</h3>
ISIS successfully established adjacency with neighbor


<h3>Recommended Actions</h3>
Check links and local and neighbor's router configuration


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| neighbor | `str` | Neighbor's NSAP or name | {{ yes }} |
| interface | `interface_name` | Interface | {{ yes }} |
| level | `str` | Level | {{ no }} |
| reason | `str` | Adjacency lost reason | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| IS-IS \| Adjacency Down](../alarm-classes-reference/network.md#network-is-is-adjacency-down) | :material-arrow-up: opening event | dispose |



## Network | IS-IS | Adjacency State Changed




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| level | `int` | System Level index | {{ no }} |
| interface | `interface_name` | Interface | {{ no }} |
| state | `int` | The IS-IS Adjacency State | {{ yes }} |
| lsp_id | `ip_address` | LSP Id | {{ no }} |




## Network | IS-IS | Adjacency Up
<h3>Symptoms</h3>
Routing table changes


<h3>Probable Causes</h3>
IS-IS successfully established adjacency with neighbor


<h3>Recommended Actions</h3>
No reaction needed


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| neighbor | `str` | Neighbor's NSAP or name | {{ yes }} |
| interface | `interface_name` | Interface | {{ yes }} |
| level | `str` | Level | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| IS-IS \| Adjacency Down](../alarm-classes-reference/network.md#network-is-is-adjacency-down) | :material-arrow-down: closing event | dispose |



## Network | IS-IS | Area Max Addresses Mismatch




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| level | `int` | System Level index | {{ no }} |
| interface | `interface_name` | Interface | {{ no }} |
| pdu_fragment | `int` | PDU fragment | {{ no }} |
| lsp_id | `ip_address` | LSP Id | {{ no }} |




## Network | IS-IS | Authentication Failure


<h3>Probable Causes</h3>
Link failure or protocol misconfiguration


<h3>Recommended Actions</h3>
Check local and neighbor router configuration


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| level | `int` | System Level index | {{ no }} |
| interface | `interface_name` | Interface | {{ no }} |
| pdu_fragment | `int` | PDU fragment | {{ yes }} |




## Network | IS-IS | Database Overload




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| level | `int` | System Level index | {{ no }} |
| state | `int` | State | {{ yes }} |




## Network | IS-IS | Protocols Supported Mismatch




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| level | `int` | System Level index | {{ no }} |
| interface | `interface_name` | Interface | {{ no }} |
| protocol | `str` | Protocols | {{ no }} |
| pdu_fragment | `int` | PDU fragment | {{ no }} |
| lsp_id | `ip_address` | LSP Id | {{ no }} |




## Network | IS-IS | SP Error




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| level | `int` | System Level index | {{ no }} |
| interface | `interface_name` | Interface | {{ no }} |
| error_type | `str` | Error type | {{ no }} |
| pdu_fragment | `int` | PDU fragment | {{ no }} |
| lsp_id | `ip_address` | LSP Id | {{ no }} |




## Network | IS-IS | Sequence Num Skip




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| level | `int` | System Level index | {{ no }} |
| interface | `interface_name` | Interface | {{ no }} |
| lsp_id | `ip_address` | LSP Id | {{ no }} |




## Network | LAG | Bundle




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Port | {{ yes }} |
| lag_interface | `interface_name` | LAG interface | {{ yes }} |




## Network | LAG | LACP Timeout




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Port | {{ yes }} |
| lag_interface | `interface_name` | LAG interface | {{ yes }} |




## Network | LAG | Unbundle




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Port | {{ yes }} |
| lag_interface | `interface_name` | LAG interface | {{ yes }} |




## Network | LBD | Loop Cleared
<h3>Symptoms</h3>
Connection restored




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | LBD interface | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| LBD \| Loop Detected](../alarm-classes-reference/network.md#network-lbd-loop-detected) | :material-arrow-down: closing event | dispose |



## Network | LBD | Loop Detected
<h3>Symptoms</h3>
Connection lost




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | LBD interface | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| LBD \| Loop Detected](../alarm-classes-reference/network.md#network-lbd-loop-detected) | :material-arrow-up: opening event | dispose |



## Network | LBD | Vlan Loop Cleared
<h3>Symptoms</h3>
Connection restore on a specific vlan




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | LBD interface | {{ yes }} |
| vlan | `int` | Vlan | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| LBD \| Vlan Loop Detected](../alarm-classes-reference/network.md#network-lbd-vlan-loop-detected) | :material-arrow-down: closing event | dispose |



## Network | LBD | Vlan Loop Detected
<h3>Symptoms</h3>
Connection lost on a specific vlan




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | LBD interface | {{ yes }} |
| vlan | `int` | Vlan | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| LBD \| Vlan Loop Detected](../alarm-classes-reference/network.md#network-lbd-vlan-loop-detected) | :material-arrow-up: opening event | dispose |



## Network | LLDP | Created New Neighbor




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Affected interface | {{ yes }} |




## Network | LLDP | LLDP Aged Out


<h3>Probable Causes</h3>
 



<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Affected interface | {{ yes }} |




## Network | LLDP | Native Vlan Not Match


<h3>Probable Causes</h3>
 


<h3>Recommended Actions</h3>
check configuration ports


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Affected interface | {{ yes }} |
| vlan | `int` | VLAN ID | {{ yes }} |
| vlan_neighbor | `int` | VLAN NEI ID | {{ yes }} |




## Network | LLDP | Remote Tables Change
<h3>Symptoms</h3>
Possible instability of network connectivity


<h3>Probable Causes</h3>
A lldpRemTablesChange notification is sent when the value of lldpStatsRemTableLastChangeTime changes.
It can beutilized by an NMS to trigger LLDP remote systems table maintenance polls.
Note that transmission of lldpRemTablesChange notifications are throttled by the agent, as specified by the 'lldpNotificationInterval' object


<h3>Recommended Actions</h3>
Large amount of deletes may indicate instable link


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| table_inserts | `int` | Number of insers per interval | {{ yes }} |
| table_deletes | `int` | Number of deletes per interval | {{ yes }} |
| table_drops | `int` | Number of drops per interval | {{ yes }} |
| table_ageouts | `int` | Number of aged entries per interval | {{ yes }} |




## Network | Link | Connection Problem
<h3>Symptoms</h3>
Poor rate, connection interrupts


<h3>Probable Causes</h3>
Cable damage, hardware or software error either from this or from another side


<h3>Recommended Actions</h3>
Check configuration, both sides of links and hardware


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Affected interface | {{ yes }} |




## Network | Link | DOM | Alarm: Out of Threshold
<h3>Symptoms</h3>
Connection lost




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `str` | Physical port | {{ yes }} |
| threshold | `str` | Threshold type | {{ no }} |
| sensor | `str` | Measured name | {{ no }} |
| ovalue | `str` | Operating value | {{ no }} |
| tvalue | `str` | Threshold value | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Link \| DOM \| Alarm: Out of Threshold](../alarm-classes-reference/network.md#network-link-dom-alarm:-out-of-threshold) | :material-arrow-up: opening event | dispose |



## Network | Link | DOM | Alarm: Out of Threshold Recovered




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `str` | Physical port | {{ yes }} |
| threshold | `str` | Threshold type | {{ no }} |
| sensor | `str` | Measured name | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Link \| DOM \| Alarm: Out of Threshold](../alarm-classes-reference/network.md#network-link-dom-alarm:-out-of-threshold) | :material-arrow-down: closing event | dispose |



## Network | Link | DOM | Warning: Out of Threshold
<h3>Symptoms</h3>
Connection lost




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `str` | Physical port | {{ yes }} |
| threshold | `str` | Threshold type | {{ no }} |
| sensor | `str` | Measured name | {{ no }} |
| ovalue | `str` | Operating value | {{ no }} |
| tvalue | `str` | Threshold value | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Link \| DOM \| Warning: Out of Threshold](../alarm-classes-reference/network.md#network-link-dom-warning:-out-of-threshold) | :material-arrow-up: opening event | dispose |



## Network | Link | DOM | Warning: Out of Threshold Recovered




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `str` | Physical port | {{ yes }} |
| threshold | `str` | Threshold type | {{ no }} |
| sensor | `str` | Measured name | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Link \| DOM \| Warning: Out of Threshold](../alarm-classes-reference/network.md#network-link-dom-warning:-out-of-threshold) | :material-arrow-down: closing event | dispose |



## Network | Link | Duplex Mismatch




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | interface name | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Link \| Duplex Mismatch](../alarm-classes-reference/network.md#network-link-duplex-mismatch) | :material-arrow-up: opening event | dispose |



## Network | Link | Err-Disable




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | interface name | {{ yes }} |
| reason | `str` | err-disable reason | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Link \| Err-Disable](../alarm-classes-reference/network.md#network-link-err-disable) | :material-arrow-up: opening event | dispose |



## Network | Link | Full-Duplex




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | interface name | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Link \| Half-Duplex](../alarm-classes-reference/network.md#network-link-half-duplex) | :material-arrow-down: closing event | dispose |



## Network | Link | Half-Duplex




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | interface name | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Link \| Half-Duplex](../alarm-classes-reference/network.md#network-link-half-duplex) | :material-arrow-up: opening event | dispose |



## Network | Link | Link Down
<h3>Symptoms</h3>
Connection lost


<h3>Probable Causes</h3>
Administrative action, cable damage, hardware or software error either from this or from another side


<h3>Recommended Actions</h3>
Check configuration, both sides of links and hardware


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Affected interface | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Link \| Link Down](../alarm-classes-reference/network.md#network-link-link-down) | :material-arrow-up: opening event | dispose |



## Network | Link | Link Flap Error Detected
<h3>Symptoms</h3>
Connection lost


<h3>Probable Causes</h3>
Cable damage, hardware or software error either from this or from another side


<h3>Recommended Actions</h3>
Check both sides of links and hardware


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Affected interface | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Link \| Err-Disable](../alarm-classes-reference/network.md#network-link-err-disable) | :material-arrow-up: opening event | dispose |



## Network | Link | Link Flap Error Recovery




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Affected interface | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Link \| Err-Disable](../alarm-classes-reference/network.md#network-link-err-disable) | :material-arrow-down: closing event | dispose |



## Network | Link | Link Up
<h3>Symptoms</h3>
Connection restored


<h3>Probable Causes</h3>
Administrative action, cable or hardware replacement


<h3>Recommended Actions</h3>
Check interfaces on both sides for possible errors


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Affected interface | {{ yes }} |
| speed | `str` | Link speed | {{ no }} |
| duplex | `str` | Duplex mode | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Link \| Link Down](../alarm-classes-reference/network.md#network-link-link-down) | :material-arrow-down: closing event | Clear Link Down |
| [Network \| Link \| Err-Disable](../alarm-classes-reference/network.md#network-link-err-disable) | :material-arrow-down: closing event | Clear Err-Disable |
| [Network \| STP \| BPDU Guard Violation](../alarm-classes-reference/network.md#network-stp-bpdu-guard-violation) | :material-arrow-down: closing event | Clear BPDU Guard Violation |
| [Network \| STP \| Root Guard Violation](../alarm-classes-reference/network.md#network-stp-root-guard-violation) | :material-arrow-down: closing event | Clear Root Guard Violation |



## Network | MAC | Duplicate MAC




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| mac | `mac` | MAC Address | {{ yes }} |
| one_interface | `interface_name` | First interface | {{ yes }} |
| two_interface | `interface_name` | Second interface | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| MAC \| Duplicate MAC](../alarm-classes-reference/network.md#network-mac-duplicate-mac) | :material-arrow-up: opening event | dispose |



## Network | MAC | Invalid MAC




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| mac | `mac` | MAC Address | {{ yes }} |
| interface | `interface_name` | Affected interface | {{ yes }} |
| vlan | `int` | Affected vlan | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| MAC \| Invalid MAC](../alarm-classes-reference/network.md#network-mac-invalid-mac) | :material-arrow-up: opening event | dispose |



## Network | MAC | Link MAC Exceed




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| mac_limit | `int` | MAC Address Limit | {{ yes }} |
| utilization | `int` | Utilization | {{ yes }} |
| interface | `interface_name` | Interface | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| MAC \| Link MAC Exceed](../alarm-classes-reference/network.md#network-mac-link-mac-exceed) | :material-arrow-up: opening event | dispose |



## Network | MAC | MAC Aged




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| mac | `mac` | MAC Address | {{ yes }} |
| vlan | `int` | VLAN | {{ no }} |
| interface | `interface_name` | Interface | {{ no }} |




## Network | MAC | MAC Flap


<h3>Probable Causes</h3>
The system found the specified host moving between the specified ports.


<h3>Recommended Actions</h3>
Examine the network for possible loops.


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| mac | `mac` | MAC Address | {{ yes }} |
| vlan | `int` | VLAN | {{ yes }} |
| from_interface | `interface_name` | From interface | {{ yes }} |
| to_interface | `interface_name` | To interface | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| MAC \| MAC Flap](../alarm-classes-reference/network.md#network-mac-mac-flap) | :material-arrow-up: opening event | dispose |



## Network | MAC | MAC Flood




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| mac | `mac` | MAC Address | {{ yes }} |
| vlan | `int` | VLAN | {{ yes }} |
| interface | `interface_name` | Interface | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| MAC \| MAC Flood](../alarm-classes-reference/network.md#network-mac-mac-flood) | :material-arrow-up: opening event | dispose |



## Network | MAC | MAC Learned




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| mac | `mac` | MAC Address | {{ yes }} |
| vlan | `int` | VLAN | {{ no }} |
| interface | `interface_name` | Interface | {{ no }} |




## Network | MAC | MAC Moved




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| mac | `mac` | MAC Address | {{ yes }} |
| vlan | `int` | VLAN | {{ no }} |
| interface | `interface_name` | Interface | {{ no }} |




## Network | MPLS | LDP Init Session Above Threshold




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| ldp_id | `int` | LDP Neighbor | {{ yes }} |
| tvalue | `int` | Threshold value | {{ yes }} |




## Network | MPLS | LDP Neighbor Down




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| neighbor | `ip_address` | LDP Neighbor | {{ yes }} |
| state | `str` | state | {{ no }} |
| reason | `str` | Reason | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| MPLS \| LDP Neighbor Down](../alarm-classes-reference/network.md#network-mpls-ldp-neighbor-down) | :material-arrow-up: opening event | dispose |



## Network | MPLS | LDP Neighbor Up




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| neighbor | `ip_address` | LDP Neighbor | {{ yes }} |
| state | `str` | state | {{ no }} |
| reason | `str` | Reason | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| MPLS \| LDP Neighbor Down](../alarm-classes-reference/network.md#network-mpls-ldp-neighbor-down) | :material-arrow-down: closing event | dispose |



## Network | MPLS | LDP Session Down




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Affected interface | {{ yes }} |
| state | `str` | state | {{ no }} |
| reason | `str` | Reason | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| MPLS \| LDP Session Down](../alarm-classes-reference/network.md#network-mpls-ldp-session-down) | :material-arrow-up: opening event | dispose |



## Network | MPLS | LDP Session Up




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Affected interface | {{ yes }} |
| state | `str` | state | {{ no }} |
| reason | `str` | Reason | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| MPLS \| LDP Session Down](../alarm-classes-reference/network.md#network-mpls-ldp-session-down) | :material-arrow-down: closing event | dispose |



## Network | MPLS | LSP Down




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | LSP name | {{ yes }} |
| reason | `str` | Reason | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| MPLS \| LSP Down](../alarm-classes-reference/network.md#network-mpls-lsp-down) | :material-arrow-up: opening event | dispose |



## Network | MPLS | LSP Path Change




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | LSP name | {{ yes }} |
| path | `str` | LSP Path | {{ no }} |




## Network | MPLS | LSP Up




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | LSP name | {{ yes }} |
| bandwidth | `int` | Bandwidth (bps) | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| MPLS \| LSP Down](../alarm-classes-reference/network.md#network-mpls-lsp-down) | :material-arrow-down: closing event | dispose |



## Network | MPLS | LSR XC Down




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| index | `int` | XC index | {{ no }} |
| lsp_id | `int` | XC LSP id | {{ no }} |
| owner | `str` | XC Owner | {{ no }} |
| admin_status | `int` | XC Admin status | {{ no }} |
| status | `int` | XC Oper status | {{ no }} |




## Network | MPLS | LSR XC Up




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| index | `int` | XC index | {{ no }} |
| lsp_id | `int` | XC LSP id | {{ no }} |
| owner | `str` | XC Owner | {{ no }} |
| admin_status | `int` | XC Admin status | {{ no }} |
| status | `int` | XC Oper status | {{ no }} |




## Network | MPLS | Link Down
<h3>Symptoms</h3>
Connection lost




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Affected interface in the VPN | {{ yes }} |
| vpn_name | `str` | Affected VPN | {{ yes }} |
| vpn_type | `str` | Affected VPN type | {{ no }} |




## Network | MPLS | Link Up
<h3>Symptoms</h3>
Connection recover




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Affected interface in the VPN | {{ yes }} |
| vpn_name | `str` | Affected VPN | {{ yes }} |
| vpn_type | `str` | Affected VPN type | {{ no }} |




## Network | MPLS | Path Down




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | Path name | {{ yes }} |
| reason | `str` | Reason | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| MPLS \| Path Down](../alarm-classes-reference/network.md#network-mpls-path-down) | :material-arrow-up: opening event | dispose |



## Network | MPLS | Path Up




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | Path name | {{ yes }} |
| bandwidth | `int` | Bandwidth (bps) | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| MPLS \| Path Down](../alarm-classes-reference/network.md#network-mpls-path-down) | :material-arrow-down: closing event | dispose |



## Network | MPLS | TDP Neighbor Down




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| neighbor | `ip_address` | TDP Neighbor | {{ yes }} |
| reason | `str` | Reason | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| MPLS \| TDP Neighbor Down](../alarm-classes-reference/network.md#network-mpls-tdp-neighbor-down) | :material-arrow-up: opening event | dispose |



## Network | MPLS | TDP Neighbor Up




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| neighbor | `ip_address` | TDP Neighbor | {{ yes }} |
| reason | `str` | Reason | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| MPLS \| TDP Neighbor Down](../alarm-classes-reference/network.md#network-mpls-tdp-neighbor-down) | :material-arrow-down: closing event | dispose |



## Network | MPLS | TE Tunnel Rerouted




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| index | `int` | Tunnel index | {{ no }} |
| name | `str` | Tunnel name | {{ no }} |
| description | `str` | Tunnel description | {{ no }} |
| admin_status | `int` | Tunnel Admin status | {{ no }} |
| status | `int` | Tunnel Oper status | {{ no }} |




## Network | MPLS | VRF Interface Down




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Vrf Interface | {{ no }} |
| vrf | `str` | vrf | {{ no }} |
| name | `str` | Vrf name | {{ no }} |
| description | `str` | Vrf description | {{ no }} |
| if_conf_status | `int` | Vrf Conf status | {{ no }} |
| vrf_oper_status | `int` | Vrf Oper status | {{ no }} |




## Network | MPLS | VRF Interface Up




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Vrf Interface | {{ no }} |
| vrf | `str` | vrf | {{ no }} |
| name | `str` | Vrf name | {{ no }} |
| description | `str` | Vrf description | {{ no }} |
| if_conf_status | `int` | Vrf Conf status | {{ no }} |
| vrf_oper_status | `int` | Vrf Oper status | {{ no }} |




## Network | MPLS | VRF Router Num Above Max Threshold




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| ovalue | `int` | Current Number Routes | {{ yes }} |
| tvalue | `int` | Configured High Rated Threshold | {{ no }} |




## Network | MPLS | VRF Router Num Above Mid Threshold




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| ovalue | `int` | Current Number Routes | {{ yes }} |
| tvalue | `int` | Configured High Rated Threshold | {{ no }} |




## Network | MSDP | Peer Down




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| peer | `ip_address` | Peer's IP | {{ yes }} |
| vrf | `str` | VRF | {{ no }} |
| reason | `str` | Reason | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| MSDP \| Peer Down](../alarm-classes-reference/network.md#network-msdp-peer-down) | :material-arrow-up: opening event | dispose |



## Network | MSDP | Peer Up




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| peer | `ip_address` | Peer's IP | {{ yes }} |
| vrf | `str` | VRF | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| MSDP \| Peer Down](../alarm-classes-reference/network.md#network-msdp-peer-down) | :material-arrow-down: closing event | dispose |



## Network | Monitor | CRC Error Cleared




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Monitor \| CRC Error Detected](../alarm-classes-reference/network.md#network-monitor-crc-error-detected) | :material-arrow-down: closing event | dispose |



## Network | Monitor | CRC Error Detected




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Monitor \| CRC Error Detected](../alarm-classes-reference/network.md#network-monitor-crc-error-detected) | :material-arrow-up: opening event | dispose |



## Network | NTP | Lost synchronization


<h3>Probable Causes</h3>
NTP synchronization with its peer has been lost


<h3>Recommended Actions</h3>
Perform the following actions:
   Check the network connection to the peer.
   Check to ensure that NTP is running on the peer.
   Check that the peer is synchronized to a stable time source.
   Check to see if the NTP packets from the peer have passed the validity tests specified in RFC1305.


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| server_name | `str` | NTP server name | {{ no }} |
| server_address | `ip_address` | NTP server IP address | {{ no }} |




## Network | NTP | NTP Server Reachable




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| server_name | `str` | NTP server name | {{ no }} |
| server_address | `ip_address` | NTP server IP address | {{ no }} |




## Network | NTP | NTP Server Unreachable




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| server_name | `str` | NTP server name | {{ no }} |
| server_address | `ip_address` | NTP server IP address | {{ no }} |




## Network | NTP | System Clock Adjusted




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| adjustment_ms | `int` | Time adjustment in msec | {{ no }} |
| server_name | `str` | NTP server name | {{ no }} |
| server_address | `ip_address` | NTP server IP address | {{ no }} |




## Network | NTP | System Clock Synchronized




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| server_name | `str` | NTP server name | {{ no }} |
| server_address | `ip_address` | NTP server IP address | {{ no }} |
| stratum | `int` | NTP server stratum | {{ no }} |




## Network | OAM | Client Clear Remote Failure


<h3>Probable Causes</h3>
The remote client received a message to clear a link fault, or a dying gasp (an unrecoverable local failure), or a critical event in the operations, administration, and maintenance Protocol Data Unit (OAMPDU).



<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |
| reason | `str` | Failure reason | {{ no }} |




## Network | OAM | Client Recieved Remote Failure


<h3>Probable Causes</h3>
The remote client indicates a Link Fault, or a Dying Gasp (an unrecoverable local failure), or a Critical Event in the OAMPDU. In the event of Link Fault, the Fnetwork administrator may consider shutting down the link.


<h3>Recommended Actions</h3>
In the event of a link fault, consider shutting down the link.


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |
| reason | `str` | Failure reason | {{ no }} |
| action | `str` | Response action | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Environment \| Total Power Loss](../alarm-classes-reference/environment.md#environment-total-power-loss) | :material-arrow-up: opening event | Total power loss |



## Network | OAM | Discovery Timeout


<h3>Probable Causes</h3>
The Ethernet OAM client on the specified interface has not received any OAMPDUs in the number of seconds for timeout that were configured by the user. The client has exited the OAM session.


<h3>Recommended Actions</h3>
No action is required.


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |




## Network | OAM | Enter Session


<h3>Probable Causes</h3>
Ethernet OAM client on the specified interface has detected a remote client and has entered the OAM session.


<h3>Recommended Actions</h3>
No action is required. 


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |




## Network | OAM | Entering Master Loopback Mode


<h3>Probable Causes</h3>
The specified interface has entered or exited loopback mode because of protocol control or an external event, such as the interface link going down.


<h3>Recommended Actions</h3>
No action is required.


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |




## Network | OAM | Entering Slave Loopback Mode


<h3>Probable Causes</h3>
The specified interface has entered or exited loopback mode because of protocol control or an external event, such as the interface link going down.


<h3>Recommended Actions</h3>
No action is required.


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |




## Network | OAM | Exit Session


<h3>Probable Causes</h3>
Ethernet OAM client on the specified interface has experienced some state change.


<h3>Recommended Actions</h3>
No action is required.


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |




## Network | OAM | Exiting Master Loopback Mode


<h3>Probable Causes</h3>
The specified interface has entered or exited loopback mode because of protocol control or an external event, such as the interface link going down.


<h3>Recommended Actions</h3>
No action is required.


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |




## Network | OAM | Exiting Slave Loopback Mode


<h3>Probable Causes</h3>
The specified interface has entered or exited loopback mode because of protocol control or an external event, such as the interface link going down.


<h3>Recommended Actions</h3>
No action is required.


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |




## Network | OAM | Monitoring Error


<h3>Probable Causes</h3>
A monitored error has been detected to have crossed the user-specified threshold.


<h3>Recommended Actions</h3>
No action is required.


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |
| error | `str` | Error type | {{ yes }} |




## Network | OSPF | Authentication Failure


<h3>Probable Causes</h3>
Link failure or protocol misconfiguration


<h3>Recommended Actions</h3>
Check local and neighbor router configuration


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| address | `ip_address` | OSPF Interface IP Address | {{ yes }} |
| interface | `interface_name` | Interface | {{ no }} |
| packet_error_type | `int` | Potential types  of  configuration  conflicts. Used  by the ospfConfigError and ospfConfigVir Error traps | {{ no }} |
| packet_src | `ip_address` | The IP address of an inbound packet that can not be identified by a neighbor instance | {{ no }} |
| packet_type | `int` | OSPF packet types | {{ no }} |
| router_id | `ip_address` | OSPF Router Id | {{ no }} |




## Network | OSPF | Interface State Changed


<h3>Probable Causes</h3>
Link failure or protocol misconfiguration


<h3>Recommended Actions</h3>
Check links and local and neighbor router configuration


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| address | `ip_address` | OSPF Interface IP Address | {{ yes }} |
| interface | `interface_name` | Interface | {{ no }} |
| state | `int` | The OSPF Interface State. | {{ yes }} |
| router_id | `ip_address` | OSPF Router Id | {{ no }} |




## Network | OSPF | LSA Max Age




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| lsdb_area | `str` | The 32-bit identifier of the area from which the LSA was received. | {{ yes }} |
| lsdb_type | `int` | The type of the link state advertisement. | {{ no }} |
| lsdb_lsid | `ip_address` | The Link State ID is an LS Type Specific field containing either a Router ID or an IP address | {{ no }} |
| lsdb_routerid | `str` | The 32 bit number that uniquely identifies the originating router in the Autonomous System. | {{ no }} |
| router_id | `ip_address` | OSPF Router Id | {{ no }} |




## Network | OSPF | LSA Originate




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| lsdb_area | `str` | The 32-bit identifier of the area from which the LSA was received. | {{ yes }} |
| lsdb_type | `int` | The type of the link state advertisement. | {{ no }} |
| lsdb_lsid | `ip_address` | The Link State ID is an LS Type Specific field containing either a Router ID or an IP address | {{ no }} |
| lsdb_routerid | `str` | The 32 bit number that uniquely identifies the originating router in the Autonomous System. | {{ no }} |
| router_id | `ip_address` | OSPF Router Id | {{ no }} |




## Network | OSPF | LSA TX Retransmit




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| lsdb_type | `int` | The type of the link state advertisement. | {{ no }} |
| lsdb_lsid | `ip_address` | The Link State ID is an LS Type Specific field containing either a Router ID or an IP address | {{ no }} |
| lsdb_routerid | `str` | The 32 bit number that uniquely identifies the originating router in the Autonomous System. | {{ no }} |
| packet_type | `int` | OSPF packet types | {{ no }} |
| router_id | `ip_address` | OSPF Router Id | {{ no }} |
| address | `ip_address` | OSPF Interface IP Address | {{ yes }} |
| interface | `interface_name` | Interface | {{ no }} |
| neighbor | `ip_address` | Neighbor's Router ID | {{ no }} |




## Network | OSPF | Neighbor Down
<h3>Symptoms</h3>
Routing table changes and possible lost of connectivity


<h3>Probable Causes</h3>
Link failure or protocol misconfiguration


<h3>Recommended Actions</h3>
Check links and local and neighbor router configuration


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| area | `str` | OSPF area | {{ no }} |
| interface | `interface_name` | Interface | {{ yes }} |
| neighbor | `ip_address` | Neighbor's Router ID | {{ yes }} |
| reason | `str` | Adjacency lost reason | {{ no }} |
| from_state | `str` | from state | {{ no }} |
| to_state | `str` | to state | {{ no }} |
| vrf | `str` | VRF | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| OSPF \| Neighbor Down](../alarm-classes-reference/network.md#network-ospf-neighbor-down) | :material-arrow-up: opening event | dispose |



## Network | OSPF | Neighbor State Changed


<h3>Probable Causes</h3>
Link failure or protocol misconfiguration


<h3>Recommended Actions</h3>
Check links and local and neighbor router configuration


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| neighbor_address | `ip_address` | OSPF neighbor IP Address | {{ yes }} |
| interface | `interface_name` | OSPF neighbor Interface | {{ no }} |
| neighbor | `ip_address` | Neighbor's Router ID | {{ yes }} |
| to_state__enum__ospf_state | `int` | The OSPF Neigbor State. | {{ yes }} |
| router_id | `ip_address` | OSPF Router Id | {{ no }} |




## Network | OSPF | Neighbor Up
<h3>Symptoms</h3>
Routing table changes


<h3>Probable Causes</h3>
An OSPF adjacency was established with the indicated neighboring router. The local router can now exchange information with it.


<h3>Recommended Actions</h3>
No specific actions needed


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| area | `str` | OSPF area | {{ no }} |
| interface | `interface_name` | Interface | {{ yes }} |
| neighbor | `ip_address` | Neighbor's Router ID | {{ yes }} |
| reason | `str` | Adjacency lost reason | {{ no }} |
| from_state | `str` | from state | {{ no }} |
| to_state | `str` | to state | {{ no }} |
| vrf | `str` | VRF | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| OSPF \| Neighbor Down](../alarm-classes-reference/network.md#network-ospf-neighbor-down) | :material-arrow-down: closing event | dispose |



## Network | PIM | DR Change
<h3>Symptoms</h3>
Some multicast flows lost


<h3>Probable Causes</h3>
PIM protocol configuration problem or link failure


<h3>Recommended Actions</h3>
Check links and local and neighbor's router configuration


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |
| from_dr | `ip_address` | From DR | {{ yes }} |
| to_dr | `ip_address` | To DR | {{ yes }} |
| vrf | `str` | VRF | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| PIM \| DR Change](../alarm-classes-reference/network.md#network-pim-dr-change) | :material-arrow-up: opening event | dispose |



## Network | PIM | Invalid RP


<h3>Probable Causes</h3>
A PIM router received a register message from another PIM router that identifies itself as the rendezvous point. If the router is not configured for another rendezvous point, it will not accept the register message.


<h3>Recommended Actions</h3>
Configure all leaf routers (first-hop routers to multicast sources) with the IP address of the valid rendezvous point.


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| pim_router | `ip_address` | PIM Router IP | {{ yes }} |
| invalid_rp | `ip_address` | Invalid RP IP | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| PIM \| Invalid RP](../alarm-classes-reference/network.md#network-pim-invalid-rp) | :material-arrow-up: opening event | dispose |



## Network | PIM | MSDP Peer Down
<h3>Symptoms</h3>
Multicast flows lost


<h3>Probable Causes</h3>
MSDP protocol configuration problem or link failure


<h3>Recommended Actions</h3>
Check links and local and neighbor's router configuration


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| peer | `ip_address` | Peer's IP | {{ yes }} |
| vrf | `str` | VRF | {{ no }} |
| reason | `str` | Reason | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| PIM \| MSDP Peer Down](../alarm-classes-reference/network.md#network-pim-msdp-peer-down) | :material-arrow-up: opening event | dispose |



## Network | PIM | MSDP Peer Up
<h3>Symptoms</h3>
Multicast flows send successfully


<h3>Probable Causes</h3>
MSDP successfully established connect with peer


<h3>Recommended Actions</h3>
No reaction needed


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| peer | `ip_address` | Peer's IP | {{ yes }} |
| vrf | `str` | VRF | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| PIM \| MSDP Peer Down](../alarm-classes-reference/network.md#network-pim-msdp-peer-down) | :material-arrow-down: closing event | dispose |



## Network | PIM | Neighbor Down
<h3>Symptoms</h3>
Multicast flows lost


<h3>Probable Causes</h3>
PIM protocol configuration problem or link failure


<h3>Recommended Actions</h3>
Check links and local and neighbor's router configuration


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |
| neighbor | `ip_address` | Neighbor's IP | {{ yes }} |
| vrf | `str` | VRF | {{ no }} |
| reason | `str` | Reason | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| PIM \| Neighbor Down](../alarm-classes-reference/network.md#network-pim-neighbor-down) | :material-arrow-up: opening event | dispose |



## Network | PIM | Neighbor Up
<h3>Symptoms</h3>
Multicast flows send successfully


<h3>Probable Causes</h3>
PIM successfully established connect with neighbor


<h3>Recommended Actions</h3>
No reaction needed


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |
| neighbor | `ip_address` | Neighbor's IP | {{ yes }} |
| vrf | `str` | VRF | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| PIM \| Neighbor Down](../alarm-classes-reference/network.md#network-pim-neighbor-down) | :material-arrow-down: closing event | dispose |



## Network | PPPOE | Accounting | Session Threshold Exceeded




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| ovalue | `int` | PPPOE Current Sessions | {{ yes }} |
| session_max | `int` | PPPOE Max Sessions | {{ yes }} |
| tvalue | `int` | PPPOE Threshold Sessions | {{ no }} |




## Network | Port Security | Port Security Violation




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |
| mac | `mac` | MAC Address | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Port Security \| Port Security Violation](../alarm-classes-reference/network.md#network-port-security-port-security-violation) | :material-arrow-up: opening event | dispose |



## Network | Port | Loss of Signal
<h3>Symptoms</h3>
Connection lost


<h3>Probable Causes</h3>
Administrative action, cable damage, hardware or software error either from this or from another side


<h3>Recommended Actions</h3>
Check configuration, both sides of links and hardware


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Affected interface | {{ yes }} |
| slot | `str` | Slot name | {{ no }} |
| card | `str` | Card name | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Port \| Loss of Signal](../alarm-classes-reference/network.md#network-port-loss-of-signal) | :material-arrow-up: opening event | dispose |



## Network | Port | Loss of Signal Resume
<h3>Symptoms</h3>
Connection lost


<h3>Probable Causes</h3>
Administrative action, cable damage, hardware or software error either from this or from another side


<h3>Recommended Actions</h3>
Check configuration, both sides of links and hardware


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Affected interface | {{ yes }} |
| slot | `str` | Slot name | {{ no }} |
| card | `str` | Card name | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Port \| Loss of Signal](../alarm-classes-reference/network.md#network-port-loss-of-signal) | :material-arrow-down: closing event | dispose |



## Network | RMON | Agent Get Error




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| index | `str` | Variable index | {{ no }} |
| variable | `str` | Requested Variable | {{ yes }} |
| reason | `str` | The reason why an internal get request for the variable monitored by this entry last failed. | {{ yes }} |




## Network | RMON | Agent Get Ok




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| index | `str` | Variable index | {{ no }} |
| variable | `str` | Requested Variable | {{ yes }} |




## Network | RSVP | Neighbor Down
<h3>Symptoms</h3>
Routing table changes and possible lost of connectivity


<h3>Probable Causes</h3>
RSVP protocol configuration problem or link failure


<h3>Recommended Actions</h3>
Check links and local and neighbor's router configuration


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |
| neighbor | `ip_address` | Neighbor's NSAP or name | {{ yes }} |
| reason | `str` | Reason | {{ no }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| RSVP \| Neighbor Down](../alarm-classes-reference/network.md#network-rsvp-neighbor-down) | :material-arrow-up: opening event | dispose |



## Network | RSVP | Neighbor Up
<h3>Symptoms</h3>
Routing table changes


<h3>Probable Causes</h3>
RSVP successfully established Neighbor with neighbor


<h3>Recommended Actions</h3>
No reaction needed


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |
| neighbor | `ip_address` | Neighbor's NSAP or name | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| RSVP \| Neighbor Down](../alarm-classes-reference/network.md#network-rsvp-neighbor-down) | :material-arrow-down: closing event | dispose |



## Network | SONET | Path Status Change




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ no }} |
| state | `str` | Status | {{ yes }} |




## Network | STP | BPDU Guard Recovery




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| STP \| BPDU Guard Violation](../alarm-classes-reference/network.md#network-stp-bpdu-guard-violation) | :material-arrow-down: closing event | dispose |



## Network | STP | BPDU Guard Violation




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| STP \| BPDU Guard Violation](../alarm-classes-reference/network.md#network-stp-bpdu-guard-violation) | :material-arrow-up: opening event | dispose |



## Network | STP | BPDU Root Violation




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| STP \| Root Guard Violation](../alarm-classes-reference/network.md#network-stp-root-guard-violation) | :material-arrow-up: opening event | dispose |



## Network | STP | Inconsistency Update STP




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| port | `interface_name` | Interface | {{ no }} |
| vlan | `int` | vlan | {{ yes }} |
| state | `str` | Status | {{ yes }} |




## Network | STP | Root Changed
<h3>Symptoms</h3>
Unexpected MAC address table cleanups, short-time traffic disruptions




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |
| vlan | `int` | VLAN ID | {{ no }} |
| instance | `int` | MST instance | {{ no }} |




## Network | STP | Root Guard Recovery




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| STP \| Root Guard Violation](../alarm-classes-reference/network.md#network-stp-root-guard-violation) | :material-arrow-down: closing event | dispose |



## Network | STP | STP Loop Cleared




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| STP \| STP Loop Detected](../alarm-classes-reference/network.md#network-stp-stp-loop-detected) | :material-arrow-down: closing event | dispose |



## Network | STP | STP Loop Detected




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| STP \| STP Loop Detected](../alarm-classes-reference/network.md#network-stp-stp-loop-detected) | :material-arrow-up: opening event | dispose |



## Network | STP | STP Port Role Changed
<h3>Symptoms</h3>
possible start of spanning tree rebuilding or interface oper status change




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |
| role | `str` | Port Role | {{ yes }} |
| vlan | `int` | VLAN ID | {{ no }} |
| instance | `int` | MST instance | {{ no }} |




## Network | STP | STP Port State Changed
<h3>Symptoms</h3>
possible start of spanning tree rebuilding or interface oper status change




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |
| state | `str` | Port State | {{ yes }} |
| vlan | `int` | VLAN ID | {{ no }} |
| instance | `int` | MST instance | {{ no }} |




## Network | STP | STP Vlan Loop Cleared




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |
| vlan | `int` | vlan | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| STP \| STP Vlan Loop Detected](../alarm-classes-reference/network.md#network-stp-stp-vlan-loop-detected) | :material-arrow-down: closing event | dispose |



## Network | STP | STP Vlan Loop Detected




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |
| vlan | `int` | vlan | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| STP \| STP Vlan Loop Detected](../alarm-classes-reference/network.md#network-stp-stp-vlan-loop-detected) | :material-arrow-up: opening event | dispose |



## Network | STP | STP instances exceeded




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| limit | `int` | Platform limit | {{ no }} |




## Network | STP | Topology Changed
<h3>Symptoms</h3>
Unexpected MAC address table cleanups, short-time traffic disruptions




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |
| vlan | `int` | VLAN ID | {{ no }} |
| instance | `int` | MST instance | {{ no }} |




## Network | Storm Control | Broadcast Storm Cleared




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Storm Control \| Broadcast Storm Detected](../alarm-classes-reference/network.md#network-storm-control-broadcast-storm-detected) | :material-arrow-down: closing event | dispose |



## Network | Storm Control | Broadcast Storm Detected




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Storm Control \| Broadcast Storm Detected](../alarm-classes-reference/network.md#network-storm-control-broadcast-storm-detected) | :material-arrow-up: opening event | dispose |



## Network | Storm Control | Multicast Storm Cleared




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Storm Control \| Multicast Storm Detected](../alarm-classes-reference/network.md#network-storm-control-multicast-storm-detected) | :material-arrow-down: closing event | dispose |



## Network | Storm Control | Multicast Storm Detected




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Storm Control \| Multicast Storm Detected](../alarm-classes-reference/network.md#network-storm-control-multicast-storm-detected) | :material-arrow-up: opening event | dispose |



## Network | Storm Control | Storm Cleared




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Storm Control \| Storm Detected](../alarm-classes-reference/network.md#network-storm-control-storm-detected) | :material-arrow-down: closing event | dispose |



## Network | Storm Control | Storm Detected




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Storm Control \| Storm Detected](../alarm-classes-reference/network.md#network-storm-control-storm-detected) | :material-arrow-up: opening event | dispose |



## Network | Storm Control | Unicast Storm Cleared




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Storm Control \| Unicast Storm Detected](../alarm-classes-reference/network.md#network-storm-control-unicast-storm-detected) | :material-arrow-down: closing event | dispose |



## Network | Storm Control | Unicast Storm Detected



<h3>Recommended Actions</h3>
Enable DLF (destination lookup failure) filter


<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Storm Control \| Unicast Storm Detected](../alarm-classes-reference/network.md#network-storm-control-unicast-storm-detected) | :material-arrow-up: opening event | dispose |



## Network | UDLD | UDLD Protocol Error Detected




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| UDLD \| UDLD Protocol Error Detected](../alarm-classes-reference/network.md#network-udld-udld-protocol-error-detected) | :material-arrow-up: opening event | dispose |



## Network | UDLD | UDLD Protocol Recovery




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |


<h3>Related Alarms</h3>
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| UDLD \| UDLD Protocol Error Detected](../alarm-classes-reference/network.md#network-udld-udld-protocol-error-detected) | :material-arrow-down: closing event | dispose |



## Network | VLAN | Trunk Port Status Changed




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| status | `str` | Port status | {{ yes }} |
| interface | `interface_name` | Interface | {{ yes }} |




## Network | VLAN | VLAN Created




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| vlan | `int` | VLAN ID | {{ yes }} |
| name | `str` | VLAN Name | {{ no }} |




## Network | VLAN | VLAN Deleted




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| vlan | `int` | VLAN ID | {{ yes }} |
| name | `str` | VLAN Name | {{ no }} |




## Network | VRRP | New Master




<h3>Variables</h3>
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |
| ip | `ip_address` | IP address | {{ yes }} |



