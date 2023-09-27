# Network | *


## Network | 802.11 | Associated




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Radio interface | {{ no }} |
| mac | `mac` | Station MAC | {{ no }} |




## Network | 802.11 | Disassociated




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Radio interface | {{ no }} |
| mac | `mac` | Station MAC | {{ no }} |
| reason | `str` | Reason | {{ no }} |




## Network | 802.11 | Max Retries




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| mac | `mac` | Station MAC | {{ no }} |




## Network | 802.11 | Roamed




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| mac | `mac` | Station MAC | {{ no }} |
| station | `mac` | Receiving station's MAC | {{ no }} |




## Network | BFD | Session Down




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | BFD interface | {{ yes }} |
| peer | `ip_address` | BFD Peer | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| BFD \| Session Down](../alarm-classes-reference/network.md#network-bfd-session-down) | :material-arrow-up: opening event | dispose |



## Network | BFD | Session Up




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | BFD interface | {{ yes }} |
| peer | `ip_address` | BFD Peer | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| BFD \| Session Down](../alarm-classes-reference/network.md#network-bfd-session-down) | :material-arrow-down: closing event | dispose |



## Network | BGP | Backward Transition




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| peer | `ip_address` | Peer | {{ yes }} |
| vrf | `str` | VRF | {{ no }} |
| as | `int` | Peer AS | {{ no }} |
| state | `str` | Transition from state | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| BGP \| Peer Down](../alarm-classes-reference/network.md#network-bgp-peer-down) | :material-arrow-up: opening event | dispose |



## Network | BGP | Established




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| peer | `ip_address` | Peer | {{ yes }} |
| vrf | `str` | VRF | {{ no }} |
| as | `int` | Peer AS | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| BGP \| Peer Down](../alarm-classes-reference/network.md#network-bgp-peer-down) | :material-arrow-down: closing event | dispose |
| [Network \| BGP \| Prefix Limit Exceeded](../alarm-classes-reference/network.md#network-bgp-prefix-limit-exceeded) | :material-arrow-down: closing event | dispose |



## Network | BGP | Max Prefixes Exceeds




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| peer | `ip_address` | Peer | {{ yes }} |
| vrf | `str` | VRF | {{ no }} |
| as | `int` | Peer AS | {{ no }} |
| recv | `int` | Prefixes recieved | {{ yes }} |
| max | `int` | Maximum prefixes | {{ no }} |




## Network | BGP | Max Prefixes Warning




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| peer | `ip_address` | Peer | {{ yes }} |
| vrf | `str` | VRF | {{ no }} |
| as | `int` | Peer AS | {{ no }} |
| recv | `int` | Prefixes recieved | {{ yes }} |
| max | `int` | Maximum prefixes | {{ no }} |




## Network | BGP | Peer Down




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| peer | `ip_address` | Peer | {{ yes }} |
| vrf | `str` | VRF | {{ no }} |
| as | `int` | Peer AS | {{ no }} |
| reason | `str` | Reason | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| BGP \| Peer Down](../alarm-classes-reference/network.md#network-bgp-peer-down) | :material-arrow-up: opening event | dispose |



## Network | BGP | Peer State Changed




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| peer | `ip_address` | Peer | {{ yes }} |
| vrf | `str` | VRF | {{ no }} |
| as | `int` | Peer AS | {{ no }} |
| from_state | `str` | Initial state | {{ no }} |
| to_state | `str` | Final state | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| BGP \| Peer Down](../alarm-classes-reference/network.md#network-bgp-peer-down) | :material-arrow-up: opening event | raise |
| [Network \| BGP \| Peer Down](../alarm-classes-reference/network.md#network-bgp-peer-down) | :material-arrow-down: closing event | clear_peer_down |
| [Network \| BGP \| Prefix Limit Exceeded](../alarm-classes-reference/network.md#network-bgp-prefix-limit-exceeded) | :material-arrow-down: closing event | clear_maxprefix |



## Network | BGP | Prefix Limit Exceeded




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| peer | `ip_address` | Peer | {{ yes }} |
| vrf | `str` | VRF | {{ no }} |
| as | `int` | Peer AS | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| BGP \| Prefix Limit Exceeded](../alarm-classes-reference/network.md#network-bgp-prefix-limit-exceeded) | :material-arrow-up: opening event | dispose |



## Network | CEF | Inconsistency Detection




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| time | `int` | sysUpTime | {{ no }} |




## Network | CEF | Peer State Changed




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| peer | `ip_address` | Peer | {{ yes }} |
| state | `str` | Peer state | {{ no }} |




## Network | CEF | Resource Failure




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| peer | `ip_address` | Peer | {{ yes }} |
| reason | `str` | Reason failed | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| CEF \| Resource Failure](../alarm-classes-reference/network.md#network-cef-resource-failure) | :material-arrow-up: opening event | dispose |



## Network | DHCP | Untrusted Server




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| ip | `ip_address` | Source IP | {{ yes }} |
| interface | `interface_name` | Source interface | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| DHCP \| Untrusted Server](../alarm-classes-reference/network.md#network-dhcp-untrusted-server) | :material-arrow-up: opening event | dispose |



## Network | DNS | Bad Query




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| ip | `ip_address` | Source IP | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| DNS \| Bad Query](../alarm-classes-reference/network.md#network-dns-bad-query) | :material-arrow-up: opening event | dispose |



## Network | DOCSIS | BPI Unautorized


### Probable Causes
An unauthorized cable modem has been deleted to enforce BPI authorization for the specified cable modem. The specified cable modem was not performing BPI negotiation.


### Recommended Actions
Check the modem interface configuration for privacy mandatory, or check for errors in the TFTP configuration file.


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| mac | `mac` | Cable Modem MAC | {{ yes }} |
| sid | `int` | Cable Modem SID | {{ no }} |
| interface | `interface_name` | Cable interface | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| DOCSIS \| BPI Unautorized](../alarm-classes-reference/network.md#network-docsis-bpi-unautorized) | :material-arrow-up: opening event | dispose |



## Network | DOCSIS | Bad Timing Offset


### Probable Causes
The cable modem is not using the correct starting offset during initial ranging, causing a zero, negative timing offset to be recorded by the CMTS for this modem. The CMTS internal algorithms that rely on the timing offset parameter will not analyze any modems that do not use the correct starting offset. The modems may not be able to function, depending on their physical location on the cable plant.


### Recommended Actions
Locate the cable modem based on the MAC address and report the initial timing offset problem to the cable modem vendor.


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| mac | `mac` | Cable Modem MAC | {{ no }} |
| sid | `int` | Cable Modem SID | {{ no }} |
| offset | `str` | Time offset | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| DOCSIS \| Bad Timing Offset](../alarm-classes-reference/network.md#network-docsis-bad-timing-offset) | :material-arrow-up: opening event | dispose |



## Network | DOCSIS | Channel Width Changed


### Probable Causes
The upstream channel frequency has been changed.



### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Cable interface | {{ yes }} |
| upstream | `str` | Upstream | {{ no }} |
| width | `str` | Channel width | {{ yes }} |




## Network | DOCSIS | Invalid CoS


### Probable Causes
The registration of the specified modem has failed because of an invalid or unsupported CoS setting.


### Recommended Actions
Ensure that the CoS fields in the configuration file are set correctly.


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| mac | `mac` | Cable Modem MAC | {{ yes }} |
| sid | `int` | Cable Modem SID | {{ no }} |
| interface | `interface_name` | Cable interface | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| DOCSIS \| Invalid CoS](../alarm-classes-reference/network.md#network-docsis-invalid-cos) | :material-arrow-up: opening event | dispose |



## Network | DOCSIS | Invalid DOCSIS Message


### Probable Causes
A cable modem that is not DOCSIS-compliant has attempted to send an invalid DOCSIS message.


### Recommended Actions
Locate the cable modem that sent this message and replace it with DOCSIS-compliant modem.


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Cable interface | {{ no }} |
| mac | `mac` | Cable Modem MAC | {{ no }} |
| sid | `int` | Cable Modem SID | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| DOCSIS \| Invalid DOCSIS Message](../alarm-classes-reference/network.md#network-docsis-invalid-docsis-message) | :material-arrow-up: opening event | dispose |



## Network | DOCSIS | Invalid QoS


### Probable Causes
The registration of the specified modem has failed because of an invalid or unsupported QoS setting.


### Recommended Actions
Ensure that the QoS fields in the configuration file are set correctly.


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| mac | `mac` | Cable Modem MAC | {{ yes }} |
| sid | `int` | Cable Modem SID | {{ no }} |
| interface | `interface_name` | Cable interface | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| DOCSIS \| Invalid QoS](../alarm-classes-reference/network.md#network-docsis-invalid-qos) | :material-arrow-up: opening event | dispose |



## Network | DOCSIS | Invalid Shared Secret


### Probable Causes
The registration of this modem has failed because of an invalid MIC string.


### Recommended Actions
Ensure that the shared secret that is in the configuration file is the same as the shared secret that is configured in the cable modem.


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| mac | `mac` | Cable Modem MAC | {{ yes }} |
| sid | `int` | Cable Modem SID | {{ no }} |
| interface | `interface_name` | Cable interface | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| DOCSIS \| Invalid Shared Secret](../alarm-classes-reference/network.md#network-docsis-invalid-shared-secret) | :material-arrow-up: opening event | dispose |



## Network | DOCSIS | Max CPE Reached


### Probable Causes
The maximum number of devices that can be attached to the cable modem has been exceeded. Therefore, the device with the specified IP address will not be added to the modem with the specified SID.


### Recommended Actions
Locate the specified device and place the device on a different cable modem with another SID.


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| mac | `mac` | CPE MAC | {{ no }} |
| ip | `ip_address` | CPE IP | {{ no }} |
| modem_mac | `mac` | Cable Modem MAC | {{ no }} |
| sid | `int` | Cable Modem SID | {{ no }} |
| interface | `interface_name` | Cable interface | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| DOCSIS \| Max CPE Reached](../alarm-classes-reference/network.md#network-docsis-max-cpe-reached) | :material-arrow-up: opening event | dispose |



## Network | DOCSIS | Maximum Capacity Reached


### Probable Causes
The currently reserved capacity on the upstream channel already exceeds its virtual reservation capacity, based on the configured subscription level limit. Increasing the subscription level limit on the current upstream channel will place you at risk of being unable to guarantee the individual reserved rates for modems since this upstream channel is already oversubscribed.


### Recommended Actions
Load-balance the modems that are requesting the reserved upstream rate on another upstream channel.


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Cable interface | {{ yes }} |
| upstream | `str` | Upstream | {{ no }} |
| cur_bps | `int` | Current bps reservation | {{ no }} |
| res_bps | `int` | Reserved bps | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| DOCSIS \| Maximum Capacity Reached](../alarm-classes-reference/network.md#network-docsis-maximum-capacity-reached) | :material-arrow-up: opening event | dispose |



## Network | DOCSIS | Maximum SIDs


### Probable Causes
The maximum number of SIDs has been allocated to the specified line card.


### Recommended Actions
Assign the cable modem to another line card.


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Cable interface | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| DOCSIS \| Maximum SIDs](../alarm-classes-reference/network.md#network-docsis-maximum-sids) | :material-arrow-up: opening event | dispose |



## Network | DOCSIS | Unregistered Modem Deleted


### Probable Causes
An unregistered cable modem has been deleted to avoid unaccounted bandwidth usage.


### Recommended Actions
Check the cable modem interface configuration for registration bypass, or check for errors in the TFTP configuration file. 


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| mac | `mac` | Cable Modem MAC | {{ yes }} |




## Network | DOCSIS | Upstream Frequency Changed


### Probable Causes
The upstream channel frequency has been changed.



### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Cable interface | {{ yes }} |
| upstream | `str` | Upstream | {{ no }} |
| frequency | `str` | Frequency | {{ yes }} |




## Network | DOCSIS | Upstream Input Power Level Changed


### Probable Causes
The upstream channel input power level has been changed.



### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Cable interface | {{ yes }} |
| upstream | `str` | Upstream | {{ no }} |
| power | `int` | Input power | {{ yes }} |




## Network | EIGRP | Neighbor Down
### Symptoms
Routing table changes and possible lost of connectivity


### Probable Causes
Link failure or protocol misconfiguration


### Recommended Actions
Check links and local and neighbor router configuration


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| as | `str` | EIGRP automonus system | {{ no }} |
| interface | `str` | Interface | {{ yes }} |
| neighbor | `ip_address` | Neighbor's Router ID | {{ yes }} |
| reason | `str` | Adjacency lost reason | {{ no }} |
| to_state | `str` | to state | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| EIGRP \| Neighbor Down](../alarm-classes-reference/network.md#network-eigrp-neighbor-down) | :material-arrow-up: opening event | dispose |



## Network | EIGRP | Neighbor Up
### Symptoms
Routing table changes


### Probable Causes
An EIGRP adjacency was established with the indicated neighboring router. The local router can now exchange information with it.


### Recommended Actions
No specific actions needed


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| as | `str` | EIGRP autonomus system | {{ no }} |
| interface | `str` | Interface | {{ yes }} |
| neighbor | `ip_address` | Neighbor's Router ID | {{ yes }} |
| reason | `str` | Adjacency lost reason | {{ no }} |
| to_state | `str` | to state | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| EIGRP \| Neighbor Down](../alarm-classes-reference/network.md#network-eigrp-neighbor-down) | :material-arrow-down: closing event | dispose |



## Network | HSRP | GRP State Changed




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| group | `str` | Group | {{ yes }} |
| interface | `interface_name` | Affected interface | {{ yes }} |
| state | `str` | HSRP state | {{ no }} |




## Network | IMPB | Dynamic IMPB entry is conflicting with static
### Symptoms
Discard user connection attemps



### Recommended Actions
Check user IP and MAC, check DHCP database


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| ip | `ip_address` | User IP | {{ yes }} |
| mac | `mac` | User MAC | {{ yes }} |
| interface | `interface_name` | Affected interface | {{ yes }} |




## Network | IMPB | Recover IMPB stop learning state
### Symptoms
Restore ability for incoming connections



### Recommended Actions
Check IMPB entry, check topology


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Affected interface | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| IMPB \| Unauthenticated IP-MAC](../alarm-classes-reference/network.md#network-impb-unauthenticated-ip-mac) | :material-arrow-down: closing event | dispose |



## Network | IMPB | Unauthenticated IP-MAC
### Symptoms
Discard user connection attempts



### Recommended Actions
Check user IP and MAC, check IMPB entry, check topology


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| ip | `ip_address` | User IP | {{ yes }} |
| mac | `mac` | User MAC | {{ yes }} |
| interface | `interface_name` | Affected interface | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| IMPB \| Unauthenticated IP-MAC](../alarm-classes-reference/network.md#network-impb-unauthenticated-ip-mac) | :material-arrow-up: opening event | dispose |



## Network | IP | ARP Moved




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | BFD interface | {{ no }} |
| ip | `ip_address` | IP | {{ yes }} |
| from_mac | `mac` | From MAC | {{ yes }} |
| to_mac | `mac` | To MAC | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| IP \| ARP Moved](../alarm-classes-reference/network.md#network-ip-arp-moved) | :material-arrow-up: opening event | dispose |



## Network | IP | ARP Zero MAC




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| ip | `ip_address` | IP | {{ yes }} |
| interface | `interface_name` | Affected interface | {{ no }} |




## Network | IP | Address Conflict




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| ip | `ip_address` | Conflicting IP | {{ yes }} |
| mac | `mac` | MAC | {{ no }} |
| interface | `interface_name` | Interface | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| IP \| Address Conflict](../alarm-classes-reference/network.md#network-ip-address-conflict) | :material-arrow-up: opening event | dispose |



## Network | IP | IP Flap




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| ip | `ip_address` | Flapped IP | {{ yes }} |
| mac | `mac` | MAC | {{ no }} |
| from_interface | `interface_name` | From interface | {{ yes }} |
| to_interface | `interface_name` | To interface | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| IP \| IP Flap](../alarm-classes-reference/network.md#network-ip-ip-flap) | :material-arrow-up: opening event | dispose |



## Network | IP | Port Exhaustion
### Symptoms
Failed to establish outgoung connection


### Probable Causes
No free TCP/UDP ports for outgoung connection


### Recommended Actions
Check applications and aging intervals


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| src_ip | `ip_address` | Source address | {{ no }} |
| dst_ip | `ip_address` | Destination address | {{ no }} |
| dst_port | `int` | Destination port | {{ no }} |
| proto | `int` | Protocol | {{ no }} |




## Network | IP | Route Limit Exceeded




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| reason | `str` | Reason | {{ no }} |




## Network | IP | Route Limit Warning




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| reason | `str` | Reason | {{ no }} |




## Network | IS-IS | Adjacency Down
### Symptoms
Routing table changes and possible lost of connectivity


### Probable Causes
ISIS successfully established adjacency with neighbor


### Recommended Actions
Check links and local and neighbor's router configuration


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| neighbor | `str` | Neighbor's NSAP or name | {{ yes }} |
| interface | `interface_name` | Interface | {{ yes }} |
| level | `str` | Level | {{ no }} |
| reason | `str` | Adjacency lost reason | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| IS-IS \| Adjacency Down](../alarm-classes-reference/network.md#network-is-is-adjacency-down) | :material-arrow-up: opening event | dispose |



## Network | IS-IS | Adjacency State Changed




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| level | `int` | System Level index | {{ no }} |
| interface | `interface_name` | Interface | {{ no }} |
| state | `int` | The IS-IS Adjacency State | {{ yes }} |
| lsp_id | `ip_address` | LSP Id | {{ no }} |




## Network | IS-IS | Adjacency Up
### Symptoms
Routing table changes


### Probable Causes
IS-IS successfully established adjacency with neighbor


### Recommended Actions
No reaction needed


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| neighbor | `str` | Neighbor's NSAP or name | {{ yes }} |
| interface | `interface_name` | Interface | {{ yes }} |
| level | `str` | Level | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| IS-IS \| Adjacency Down](../alarm-classes-reference/network.md#network-is-is-adjacency-down) | :material-arrow-down: closing event | dispose |



## Network | IS-IS | Area Max Addresses Mismatch




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| level | `int` | System Level index | {{ no }} |
| interface | `interface_name` | Interface | {{ no }} |
| pdu_fragment | `int` | PDU fragment | {{ no }} |
| lsp_id | `ip_address` | LSP Id | {{ no }} |




## Network | IS-IS | Authentication Failure


### Probable Causes
Link failure or protocol misconfiguration


### Recommended Actions
Check local and neighbor router configuration


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| level | `int` | System Level index | {{ no }} |
| interface | `interface_name` | Interface | {{ no }} |
| pdu_fragment | `int` | PDU fragment | {{ yes }} |




## Network | IS-IS | Database Overload




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| level | `int` | System Level index | {{ no }} |
| state | `int` | State | {{ yes }} |




## Network | IS-IS | Protocols Supported Mismatch




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| level | `int` | System Level index | {{ no }} |
| interface | `interface_name` | Interface | {{ no }} |
| protocol | `str` | Protocols | {{ no }} |
| pdu_fragment | `int` | PDU fragment | {{ no }} |
| lsp_id | `ip_address` | LSP Id | {{ no }} |




## Network | IS-IS | SP Error




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| level | `int` | System Level index | {{ no }} |
| interface | `interface_name` | Interface | {{ no }} |
| error_type | `str` | Error type | {{ no }} |
| pdu_fragment | `int` | PDU fragment | {{ no }} |
| lsp_id | `ip_address` | LSP Id | {{ no }} |




## Network | IS-IS | Sequence Num Skip




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| level | `int` | System Level index | {{ no }} |
| interface | `interface_name` | Interface | {{ no }} |
| lsp_id | `ip_address` | LSP Id | {{ no }} |




## Network | LAG | Bundle




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Port | {{ yes }} |
| lag_interface | `interface_name` | LAG interface | {{ yes }} |




## Network | LAG | LACP Timeout




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Port | {{ yes }} |
| lag_interface | `interface_name` | LAG interface | {{ yes }} |




## Network | LAG | Unbundle




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Port | {{ yes }} |
| lag_interface | `interface_name` | LAG interface | {{ yes }} |




## Network | LBD | Loop Cleared
### Symptoms
Connection restored




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | LBD interface | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| LBD \| Loop Detected](../alarm-classes-reference/network.md#network-lbd-loop-detected) | :material-arrow-down: closing event | dispose |



## Network | LBD | Loop Detected
### Symptoms
Connection lost




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | LBD interface | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| LBD \| Loop Detected](../alarm-classes-reference/network.md#network-lbd-loop-detected) | :material-arrow-up: opening event | dispose |



## Network | LBD | Vlan Loop Cleared
### Symptoms
Connection restore on a specific vlan




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | LBD interface | {{ yes }} |
| vlan | `int` | Vlan | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| LBD \| Vlan Loop Detected](../alarm-classes-reference/network.md#network-lbd-vlan-loop-detected) | :material-arrow-down: closing event | dispose |



## Network | LBD | Vlan Loop Detected
### Symptoms
Connection lost on a specific vlan




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | LBD interface | {{ yes }} |
| vlan | `int` | Vlan | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| LBD \| Vlan Loop Detected](../alarm-classes-reference/network.md#network-lbd-vlan-loop-detected) | :material-arrow-up: opening event | dispose |



## Network | LLDP | Created New Neighbor




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Affected interface | {{ yes }} |




## Network | LLDP | LLDP Aged Out


### Probable Causes
 



### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Affected interface | {{ yes }} |




## Network | LLDP | Native Vlan Not Match


### Probable Causes
 


### Recommended Actions
check configuration ports


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Affected interface | {{ yes }} |
| vlan | `int` | VLAN ID | {{ yes }} |
| vlan_neighbor | `int` | VLAN NEI ID | {{ yes }} |




## Network | LLDP | Remote Tables Change
### Symptoms
Possible instability of network connectivity


### Probable Causes
A lldpRemTablesChange notification is sent when the value of lldpStatsRemTableLastChangeTime changes.
It can beutilized by an NMS to trigger LLDP remote systems table maintenance polls.
Note that transmission of lldpRemTablesChange notifications are throttled by the agent, as specified by the 'lldpNotificationInterval' object


### Recommended Actions
Large amount of deletes may indicate instable link


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| table_inserts | `int` | Number of insers per interval | {{ yes }} |
| table_deletes | `int` | Number of deletes per interval | {{ yes }} |
| table_drops | `int` | Number of drops per interval | {{ yes }} |
| table_ageouts | `int` | Number of aged entries per interval | {{ yes }} |




## Network | Link | Connection Problem
### Symptoms
Poor rate, connection interrupts


### Probable Causes
Cable damage, hardware or software error either from this or from another side


### Recommended Actions
Check configuration, both sides of links and hardware


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Affected interface | {{ yes }} |




## Network | Link | DOM | Alarm: Out of Threshold
### Symptoms
Connection lost




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `str` | Physical port | {{ yes }} |
| threshold | `str` | Threshold type | {{ no }} |
| sensor | `str` | Measured name | {{ no }} |
| ovalue | `str` | Operating value | {{ no }} |
| tvalue | `str` | Threshold value | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Link \| DOM \| Alarm: Out of Threshold](../alarm-classes-reference/network.md#network-link-dom-alarm:-out-of-threshold) | :material-arrow-up: opening event | dispose |



## Network | Link | DOM | Alarm: Out of Threshold Recovered




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `str` | Physical port | {{ yes }} |
| threshold | `str` | Threshold type | {{ no }} |
| sensor | `str` | Measured name | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Link \| DOM \| Alarm: Out of Threshold](../alarm-classes-reference/network.md#network-link-dom-alarm:-out-of-threshold) | :material-arrow-down: closing event | dispose |



## Network | Link | DOM | Warning: Out of Threshold
### Symptoms
Connection lost




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `str` | Physical port | {{ yes }} |
| threshold | `str` | Threshold type | {{ no }} |
| sensor | `str` | Measured name | {{ no }} |
| ovalue | `str` | Operating value | {{ no }} |
| tvalue | `str` | Threshold value | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Link \| DOM \| Warning: Out of Threshold](../alarm-classes-reference/network.md#network-link-dom-warning:-out-of-threshold) | :material-arrow-up: opening event | dispose |



## Network | Link | DOM | Warning: Out of Threshold Recovered




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `str` | Physical port | {{ yes }} |
| threshold | `str` | Threshold type | {{ no }} |
| sensor | `str` | Measured name | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Link \| DOM \| Warning: Out of Threshold](../alarm-classes-reference/network.md#network-link-dom-warning:-out-of-threshold) | :material-arrow-down: closing event | dispose |



## Network | Link | Duplex Mismatch




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | interface name | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Link \| Duplex Mismatch](../alarm-classes-reference/network.md#network-link-duplex-mismatch) | :material-arrow-up: opening event | dispose |



## Network | Link | Err-Disable




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | interface name | {{ yes }} |
| reason | `str` | err-disable reason | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Link \| Err-Disable](../alarm-classes-reference/network.md#network-link-err-disable) | :material-arrow-up: opening event | dispose |



## Network | Link | Full-Duplex




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | interface name | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Link \| Half-Duplex](../alarm-classes-reference/network.md#network-link-half-duplex) | :material-arrow-down: closing event | dispose |



## Network | Link | Half-Duplex




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | interface name | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Link \| Half-Duplex](../alarm-classes-reference/network.md#network-link-half-duplex) | :material-arrow-up: opening event | dispose |



## Network | Link | Link Down
### Symptoms
Connection lost


### Probable Causes
Administrative action, cable damage, hardware or software error either from this or from another side


### Recommended Actions
Check configuration, both sides of links and hardware


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Affected interface | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Link \| Link Down](../alarm-classes-reference/network.md#network-link-link-down) | :material-arrow-up: opening event | dispose |



## Network | Link | Link Flap Error Detected
### Symptoms
Connection lost


### Probable Causes
Cable damage, hardware or software error either from this or from another side


### Recommended Actions
Check both sides of links and hardware


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Affected interface | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Link \| Err-Disable](../alarm-classes-reference/network.md#network-link-err-disable) | :material-arrow-up: opening event | dispose |



## Network | Link | Link Flap Error Recovery




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Affected interface | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Link \| Err-Disable](../alarm-classes-reference/network.md#network-link-err-disable) | :material-arrow-down: closing event | dispose |



## Network | Link | Link Up
### Symptoms
Connection restored


### Probable Causes
Administrative action, cable or hardware replacement


### Recommended Actions
Check interfaces on both sides for possible errors


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Affected interface | {{ yes }} |
| speed | `str` | Link speed | {{ no }} |
| duplex | `str` | Duplex mode | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Link \| Link Down](../alarm-classes-reference/network.md#network-link-link-down) | :material-arrow-down: closing event | Clear Link Down |
| [Network \| Link \| Err-Disable](../alarm-classes-reference/network.md#network-link-err-disable) | :material-arrow-down: closing event | Clear Err-Disable |
| [Network \| STP \| BPDU Guard Violation](../alarm-classes-reference/network.md#network-stp-bpdu-guard-violation) | :material-arrow-down: closing event | Clear BPDU Guard Violation |
| [Network \| STP \| Root Guard Violation](../alarm-classes-reference/network.md#network-stp-root-guard-violation) | :material-arrow-down: closing event | Clear Root Guard Violation |



## Network | MAC | Duplicate MAC




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| mac | `mac` | MAC Address | {{ yes }} |
| one_interface | `interface_name` | First interface | {{ yes }} |
| two_interface | `interface_name` | Second interface | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| MAC \| Duplicate MAC](../alarm-classes-reference/network.md#network-mac-duplicate-mac) | :material-arrow-up: opening event | dispose |



## Network | MAC | Invalid MAC




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| mac | `mac` | MAC Address | {{ yes }} |
| interface | `interface_name` | Affected interface | {{ yes }} |
| vlan | `int` | Affected vlan | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| MAC \| Invalid MAC](../alarm-classes-reference/network.md#network-mac-invalid-mac) | :material-arrow-up: opening event | dispose |



## Network | MAC | Link MAC Exceed




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| mac_limit | `int` | MAC Address Limit | {{ yes }} |
| utilization | `int` | Utilization | {{ yes }} |
| interface | `interface_name` | Interface | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| MAC \| Link MAC Exceed](../alarm-classes-reference/network.md#network-mac-link-mac-exceed) | :material-arrow-up: opening event | dispose |



## Network | MAC | MAC Aged




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| mac | `mac` | MAC Address | {{ yes }} |
| vlan | `int` | VLAN | {{ no }} |
| interface | `interface_name` | Interface | {{ no }} |




## Network | MAC | MAC Flap


### Probable Causes
The system found the specified host moving between the specified ports.


### Recommended Actions
Examine the network for possible loops.


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| mac | `mac` | MAC Address | {{ yes }} |
| vlan | `int` | VLAN | {{ yes }} |
| from_interface | `interface_name` | From interface | {{ yes }} |
| to_interface | `interface_name` | To interface | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| MAC \| MAC Flap](../alarm-classes-reference/network.md#network-mac-mac-flap) | :material-arrow-up: opening event | dispose |



## Network | MAC | MAC Flood




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| mac | `mac` | MAC Address | {{ yes }} |
| vlan | `int` | VLAN | {{ yes }} |
| interface | `interface_name` | Interface | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| MAC \| MAC Flood](../alarm-classes-reference/network.md#network-mac-mac-flood) | :material-arrow-up: opening event | dispose |



## Network | MAC | MAC Learned




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| mac | `mac` | MAC Address | {{ yes }} |
| vlan | `int` | VLAN | {{ no }} |
| interface | `interface_name` | Interface | {{ no }} |




## Network | MAC | MAC Moved




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| mac | `mac` | MAC Address | {{ yes }} |
| vlan | `int` | VLAN | {{ no }} |
| interface | `interface_name` | Interface | {{ no }} |




## Network | MPLS | LDP Init Session Above Threshold




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| ldp_id | `int` | LDP Neighbor | {{ yes }} |
| tvalue | `int` | Threshold value | {{ yes }} |




## Network | MPLS | LDP Neighbor Down




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| neighbor | `ip_address` | LDP Neighbor | {{ yes }} |
| state | `str` | state | {{ no }} |
| reason | `str` | Reason | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| MPLS \| LDP Neighbor Down](../alarm-classes-reference/network.md#network-mpls-ldp-neighbor-down) | :material-arrow-up: opening event | dispose |



## Network | MPLS | LDP Neighbor Up




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| neighbor | `ip_address` | LDP Neighbor | {{ yes }} |
| state | `str` | state | {{ no }} |
| reason | `str` | Reason | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| MPLS \| LDP Neighbor Down](../alarm-classes-reference/network.md#network-mpls-ldp-neighbor-down) | :material-arrow-down: closing event | dispose |



## Network | MPLS | LDP Session Down




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Affected interface | {{ yes }} |
| state | `str` | state | {{ no }} |
| reason | `str` | Reason | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| MPLS \| LDP Session Down](../alarm-classes-reference/network.md#network-mpls-ldp-session-down) | :material-arrow-up: opening event | dispose |



## Network | MPLS | LDP Session Up




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Affected interface | {{ yes }} |
| state | `str` | state | {{ no }} |
| reason | `str` | Reason | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| MPLS \| LDP Session Down](../alarm-classes-reference/network.md#network-mpls-ldp-session-down) | :material-arrow-down: closing event | dispose |



## Network | MPLS | LSP Down




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | LSP name | {{ yes }} |
| reason | `str` | Reason | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| MPLS \| LSP Down](../alarm-classes-reference/network.md#network-mpls-lsp-down) | :material-arrow-up: opening event | dispose |



## Network | MPLS | LSP Path Change




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | LSP name | {{ yes }} |
| path | `str` | LSP Path | {{ no }} |




## Network | MPLS | LSP Up




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | LSP name | {{ yes }} |
| bandwidth | `int` | Bandwidth (bps) | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| MPLS \| LSP Down](../alarm-classes-reference/network.md#network-mpls-lsp-down) | :material-arrow-down: closing event | dispose |



## Network | MPLS | LSR XC Down




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| index | `int` | XC index | {{ no }} |
| lsp_id | `int` | XC LSP id | {{ no }} |
| owner | `str` | XC Owner | {{ no }} |
| admin_status | `int` | XC Admin status | {{ no }} |
| status | `int` | XC Oper status | {{ no }} |




## Network | MPLS | LSR XC Up




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| index | `int` | XC index | {{ no }} |
| lsp_id | `int` | XC LSP id | {{ no }} |
| owner | `str` | XC Owner | {{ no }} |
| admin_status | `int` | XC Admin status | {{ no }} |
| status | `int` | XC Oper status | {{ no }} |




## Network | MPLS | Link Down
### Symptoms
Connection lost




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Affected interface in the VPN | {{ yes }} |
| vpn_name | `str` | Affected VPN | {{ yes }} |
| vpn_type | `str` | Affected VPN type | {{ no }} |




## Network | MPLS | Link Up
### Symptoms
Connection recover




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Affected interface in the VPN | {{ yes }} |
| vpn_name | `str` | Affected VPN | {{ yes }} |
| vpn_type | `str` | Affected VPN type | {{ no }} |




## Network | MPLS | Path Down




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | Path name | {{ yes }} |
| reason | `str` | Reason | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| MPLS \| Path Down](../alarm-classes-reference/network.md#network-mpls-path-down) | :material-arrow-up: opening event | dispose |



## Network | MPLS | Path Up




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| name | `str` | Path name | {{ yes }} |
| bandwidth | `int` | Bandwidth (bps) | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| MPLS \| Path Down](../alarm-classes-reference/network.md#network-mpls-path-down) | :material-arrow-down: closing event | dispose |



## Network | MPLS | TDP Neighbor Down




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| neighbor | `ip_address` | TDP Neighbor | {{ yes }} |
| reason | `str` | Reason | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| MPLS \| TDP Neighbor Down](../alarm-classes-reference/network.md#network-mpls-tdp-neighbor-down) | :material-arrow-up: opening event | dispose |



## Network | MPLS | TDP Neighbor Up




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| neighbor | `ip_address` | TDP Neighbor | {{ yes }} |
| reason | `str` | Reason | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| MPLS \| TDP Neighbor Down](../alarm-classes-reference/network.md#network-mpls-tdp-neighbor-down) | :material-arrow-down: closing event | dispose |



## Network | MPLS | TE Tunnel Rerouted




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| index | `int` | Tunnel index | {{ no }} |
| name | `str` | Tunnel name | {{ no }} |
| description | `str` | Tunnel description | {{ no }} |
| admin_status | `int` | Tunnel Admin status | {{ no }} |
| status | `int` | Tunnel Oper status | {{ no }} |




## Network | MPLS | VRF Interface Down




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Vrf Interface | {{ no }} |
| vrf | `str` | vrf | {{ no }} |
| name | `str` | Vrf name | {{ no }} |
| description | `str` | Vrf description | {{ no }} |
| if_conf_status | `int` | Vrf Conf status | {{ no }} |
| vrf_oper_status | `int` | Vrf Oper status | {{ no }} |




## Network | MPLS | VRF Interface Up




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Vrf Interface | {{ no }} |
| vrf | `str` | vrf | {{ no }} |
| name | `str` | Vrf name | {{ no }} |
| description | `str` | Vrf description | {{ no }} |
| if_conf_status | `int` | Vrf Conf status | {{ no }} |
| vrf_oper_status | `int` | Vrf Oper status | {{ no }} |




## Network | MPLS | VRF Router Num Above Max Threshold




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| ovalue | `int` | Current Number Routes | {{ yes }} |
| tvalue | `int` | Configured High Rated Threshold | {{ no }} |




## Network | MPLS | VRF Router Num Above Mid Threshold




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| ovalue | `int` | Current Number Routes | {{ yes }} |
| tvalue | `int` | Configured High Rated Threshold | {{ no }} |




## Network | MSDP | Peer Down




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| peer | `ip_address` | Peer's IP | {{ yes }} |
| vrf | `str` | VRF | {{ no }} |
| reason | `str` | Reason | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| MSDP \| Peer Down](../alarm-classes-reference/network.md#network-msdp-peer-down) | :material-arrow-up: opening event | dispose |



## Network | MSDP | Peer Up




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| peer | `ip_address` | Peer's IP | {{ yes }} |
| vrf | `str` | VRF | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| MSDP \| Peer Down](../alarm-classes-reference/network.md#network-msdp-peer-down) | :material-arrow-down: closing event | dispose |



## Network | Monitor | CRC Error Cleared




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Monitor \| CRC Error Detected](../alarm-classes-reference/network.md#network-monitor-crc-error-detected) | :material-arrow-down: closing event | dispose |



## Network | Monitor | CRC Error Detected




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Monitor \| CRC Error Detected](../alarm-classes-reference/network.md#network-monitor-crc-error-detected) | :material-arrow-up: opening event | dispose |



## Network | NTP | Lost synchronization


### Probable Causes
NTP synchronization with its peer has been lost


### Recommended Actions
Perform the following actions:
   Check the network connection to the peer.
   Check to ensure that NTP is running on the peer.
   Check that the peer is synchronized to a stable time source.
   Check to see if the NTP packets from the peer have passed the validity tests specified in RFC1305.


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| server_name | `str` | NTP server name | {{ no }} |
| server_address | `ip_address` | NTP server IP address | {{ no }} |




## Network | NTP | NTP Server Reachable




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| server_name | `str` | NTP server name | {{ no }} |
| server_address | `ip_address` | NTP server IP address | {{ no }} |




## Network | NTP | NTP Server Unreachable




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| server_name | `str` | NTP server name | {{ no }} |
| server_address | `ip_address` | NTP server IP address | {{ no }} |




## Network | NTP | System Clock Adjusted




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| adjustment_ms | `int` | Time adjustment in msec | {{ no }} |
| server_name | `str` | NTP server name | {{ no }} |
| server_address | `ip_address` | NTP server IP address | {{ no }} |




## Network | NTP | System Clock Synchronized




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| server_name | `str` | NTP server name | {{ no }} |
| server_address | `ip_address` | NTP server IP address | {{ no }} |
| stratum | `int` | NTP server stratum | {{ no }} |




## Network | OAM | Client Clear Remote Failure


### Probable Causes
The remote client received a message to clear a link fault, or a dying gasp (an unrecoverable local failure), or a critical event in the operations, administration, and maintenance Protocol Data Unit (OAMPDU).



### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |
| reason | `str` | Failure reason | {{ no }} |




## Network | OAM | Client Recieved Remote Failure


### Probable Causes
The remote client indicates a Link Fault, or a Dying Gasp (an unrecoverable local failure), or a Critical Event in the OAMPDU. In the event of Link Fault, the Fnetwork administrator may consider shutting down the link.


### Recommended Actions
In the event of a link fault, consider shutting down the link.


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |
| reason | `str` | Failure reason | {{ no }} |
| action | `str` | Response action | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Environment \| Total Power Loss](../alarm-classes-reference/environment.md#environment-total-power-loss) | :material-arrow-up: opening event | Total power loss |



## Network | OAM | Discovery Timeout


### Probable Causes
The Ethernet OAM client on the specified interface has not received any OAMPDUs in the number of seconds for timeout that were configured by the user. The client has exited the OAM session.


### Recommended Actions
No action is required.


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |




## Network | OAM | Enter Session


### Probable Causes
Ethernet OAM client on the specified interface has detected a remote client and has entered the OAM session.


### Recommended Actions
No action is required. 


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |




## Network | OAM | Entering Master Loopback Mode


### Probable Causes
The specified interface has entered or exited loopback mode because of protocol control or an external event, such as the interface link going down.


### Recommended Actions
No action is required.


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |




## Network | OAM | Entering Slave Loopback Mode


### Probable Causes
The specified interface has entered or exited loopback mode because of protocol control or an external event, such as the interface link going down.


### Recommended Actions
No action is required.


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |




## Network | OAM | Exit Session


### Probable Causes
Ethernet OAM client on the specified interface has experienced some state change.


### Recommended Actions
No action is required.


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |




## Network | OAM | Exiting Master Loopback Mode


### Probable Causes
The specified interface has entered or exited loopback mode because of protocol control or an external event, such as the interface link going down.


### Recommended Actions
No action is required.


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |




## Network | OAM | Exiting Slave Loopback Mode


### Probable Causes
The specified interface has entered or exited loopback mode because of protocol control or an external event, such as the interface link going down.


### Recommended Actions
No action is required.


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |




## Network | OAM | Monitoring Error


### Probable Causes
A monitored error has been detected to have crossed the user-specified threshold.


### Recommended Actions
No action is required.


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |
| error | `str` | Error type | {{ yes }} |




## Network | OSPF | Authentication Failure


### Probable Causes
Link failure or protocol misconfiguration


### Recommended Actions
Check local and neighbor router configuration


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| address | `ip_address` | OSPF Interface IP Address | {{ yes }} |
| interface | `interface_name` | Interface | {{ no }} |
| packet_error_type | `int` | Potential types  of  configuration  conflicts. Used  by the ospfConfigError and ospfConfigVir Error traps | {{ no }} |
| packet_src | `ip_address` | The IP address of an inbound packet that can not be identified by a neighbor instance | {{ no }} |
| packet_type | `int` | OSPF packet types | {{ no }} |
| router_id | `ip_address` | OSPF Router Id | {{ no }} |




## Network | OSPF | Interface State Changed


### Probable Causes
Link failure or protocol misconfiguration


### Recommended Actions
Check links and local and neighbor router configuration


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| address | `ip_address` | OSPF Interface IP Address | {{ yes }} |
| interface | `interface_name` | Interface | {{ no }} |
| state | `int` | The OSPF Interface State. | {{ yes }} |
| router_id | `ip_address` | OSPF Router Id | {{ no }} |




## Network | OSPF | LSA Max Age




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| lsdb_area | `str` | The 32-bit identifier of the area from which the LSA was received. | {{ yes }} |
| lsdb_type | `int` | The type of the link state advertisement. | {{ no }} |
| lsdb_lsid | `ip_address` | The Link State ID is an LS Type Specific field containing either a Router ID or an IP address | {{ no }} |
| lsdb_routerid | `str` | The 32 bit number that uniquely identifies the originating router in the Autonomous System. | {{ no }} |
| router_id | `ip_address` | OSPF Router Id | {{ no }} |




## Network | OSPF | LSA Originate




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| lsdb_area | `str` | The 32-bit identifier of the area from which the LSA was received. | {{ yes }} |
| lsdb_type | `int` | The type of the link state advertisement. | {{ no }} |
| lsdb_lsid | `ip_address` | The Link State ID is an LS Type Specific field containing either a Router ID or an IP address | {{ no }} |
| lsdb_routerid | `str` | The 32 bit number that uniquely identifies the originating router in the Autonomous System. | {{ no }} |
| router_id | `ip_address` | OSPF Router Id | {{ no }} |




## Network | OSPF | LSA TX Retransmit




### Variables
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
### Symptoms
Routing table changes and possible lost of connectivity


### Probable Causes
Link failure or protocol misconfiguration


### Recommended Actions
Check links and local and neighbor router configuration


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| area | `str` | OSPF area | {{ no }} |
| interface | `interface_name` | Interface | {{ yes }} |
| neighbor | `ip_address` | Neighbor's Router ID | {{ yes }} |
| reason | `str` | Adjacency lost reason | {{ no }} |
| from_state | `str` | from state | {{ no }} |
| to_state | `str` | to state | {{ no }} |
| vrf | `str` | VRF | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| OSPF \| Neighbor Down](../alarm-classes-reference/network.md#network-ospf-neighbor-down) | :material-arrow-up: opening event | dispose |



## Network | OSPF | Neighbor State Changed


### Probable Causes
Link failure or protocol misconfiguration


### Recommended Actions
Check links and local and neighbor router configuration


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| neighbor_address | `ip_address` | OSPF neighbor IP Address | {{ yes }} |
| interface | `interface_name` | OSPF neighbor Interface | {{ no }} |
| neighbor | `ip_address` | Neighbor's Router ID | {{ yes }} |
| to_state__enum__ospf_state | `int` | The OSPF Neigbor State. | {{ yes }} |
| router_id | `ip_address` | OSPF Router Id | {{ no }} |




## Network | OSPF | Neighbor Up
### Symptoms
Routing table changes


### Probable Causes
An OSPF adjacency was established with the indicated neighboring router. The local router can now exchange information with it.


### Recommended Actions
No specific actions needed


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| area | `str` | OSPF area | {{ no }} |
| interface | `interface_name` | Interface | {{ yes }} |
| neighbor | `ip_address` | Neighbor's Router ID | {{ yes }} |
| reason | `str` | Adjacency lost reason | {{ no }} |
| from_state | `str` | from state | {{ no }} |
| to_state | `str` | to state | {{ no }} |
| vrf | `str` | VRF | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| OSPF \| Neighbor Down](../alarm-classes-reference/network.md#network-ospf-neighbor-down) | :material-arrow-down: closing event | dispose |



## Network | PIM | DR Change
### Symptoms
Some multicast flows lost


### Probable Causes
PIM protocol configuration problem or link failure


### Recommended Actions
Check links and local and neighbor's router configuration


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |
| from_dr | `ip_address` | From DR | {{ yes }} |
| to_dr | `ip_address` | To DR | {{ yes }} |
| vrf | `str` | VRF | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| PIM \| DR Change](../alarm-classes-reference/network.md#network-pim-dr-change) | :material-arrow-up: opening event | dispose |



## Network | PIM | Invalid RP


### Probable Causes
A PIM router received a register message from another PIM router that identifies itself as the rendezvous point. If the router is not configured for another rendezvous point, it will not accept the register message.


### Recommended Actions
Configure all leaf routers (first-hop routers to multicast sources) with the IP address of the valid rendezvous point.


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| pim_router | `ip_address` | PIM Router IP | {{ yes }} |
| invalid_rp | `ip_address` | Invalid RP IP | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| PIM \| Invalid RP](../alarm-classes-reference/network.md#network-pim-invalid-rp) | :material-arrow-up: opening event | dispose |



## Network | PIM | MSDP Peer Down
### Symptoms
Multicast flows lost


### Probable Causes
MSDP protocol configuration problem or link failure


### Recommended Actions
Check links and local and neighbor's router configuration


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| peer | `ip_address` | Peer's IP | {{ yes }} |
| vrf | `str` | VRF | {{ no }} |
| reason | `str` | Reason | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| PIM \| MSDP Peer Down](../alarm-classes-reference/network.md#network-pim-msdp-peer-down) | :material-arrow-up: opening event | dispose |



## Network | PIM | MSDP Peer Up
### Symptoms
Multicast flows send successfully


### Probable Causes
MSDP successfully established connect with peer


### Recommended Actions
No reaction needed


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| peer | `ip_address` | Peer's IP | {{ yes }} |
| vrf | `str` | VRF | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| PIM \| MSDP Peer Down](../alarm-classes-reference/network.md#network-pim-msdp-peer-down) | :material-arrow-down: closing event | dispose |



## Network | PIM | Neighbor Down
### Symptoms
Multicast flows lost


### Probable Causes
PIM protocol configuration problem or link failure


### Recommended Actions
Check links and local and neighbor's router configuration


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |
| neighbor | `ip_address` | Neighbor's IP | {{ yes }} |
| vrf | `str` | VRF | {{ no }} |
| reason | `str` | Reason | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| PIM \| Neighbor Down](../alarm-classes-reference/network.md#network-pim-neighbor-down) | :material-arrow-up: opening event | dispose |



## Network | PIM | Neighbor Up
### Symptoms
Multicast flows send successfully


### Probable Causes
PIM successfully established connect with neighbor


### Recommended Actions
No reaction needed


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |
| neighbor | `ip_address` | Neighbor's IP | {{ yes }} |
| vrf | `str` | VRF | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| PIM \| Neighbor Down](../alarm-classes-reference/network.md#network-pim-neighbor-down) | :material-arrow-down: closing event | dispose |



## Network | PPPOE | Accounting | Session Threshold Exceeded




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| ovalue | `int` | PPPOE Current Sessions | {{ yes }} |
| session_max | `int` | PPPOE Max Sessions | {{ yes }} |
| tvalue | `int` | PPPOE Threshold Sessions | {{ no }} |




## Network | Port Security | Port Security Violation




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |
| mac | `mac` | MAC Address | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Port Security \| Port Security Violation](../alarm-classes-reference/network.md#network-port-security-port-security-violation) | :material-arrow-up: opening event | dispose |



## Network | Port | Loss of Signal
### Symptoms
Connection lost


### Probable Causes
Administrative action, cable damage, hardware or software error either from this or from another side


### Recommended Actions
Check configuration, both sides of links and hardware


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Affected interface | {{ yes }} |
| slot | `str` | Slot name | {{ no }} |
| card | `str` | Card name | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Port \| Loss of Signal](../alarm-classes-reference/network.md#network-port-loss-of-signal) | :material-arrow-up: opening event | dispose |



## Network | Port | Loss of Signal Resume
### Symptoms
Connection lost


### Probable Causes
Administrative action, cable damage, hardware or software error either from this or from another side


### Recommended Actions
Check configuration, both sides of links and hardware


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Affected interface | {{ yes }} |
| slot | `str` | Slot name | {{ no }} |
| card | `str` | Card name | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Port \| Loss of Signal](../alarm-classes-reference/network.md#network-port-loss-of-signal) | :material-arrow-down: closing event | dispose |



## Network | RMON | Agent Get Error




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| index | `str` | Variable index | {{ no }} |
| variable | `str` | Requested Variable | {{ yes }} |
| reason | `str` | The reason why an internal get request for the variable monitored by this entry last failed. | {{ yes }} |




## Network | RMON | Agent Get Ok




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| index | `str` | Variable index | {{ no }} |
| variable | `str` | Requested Variable | {{ yes }} |




## Network | RSVP | Neighbor Down
### Symptoms
Routing table changes and possible lost of connectivity


### Probable Causes
RSVP protocol configuration problem or link failure


### Recommended Actions
Check links and local and neighbor's router configuration


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |
| neighbor | `ip_address` | Neighbor's NSAP or name | {{ yes }} |
| reason | `str` | Reason | {{ no }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| RSVP \| Neighbor Down](../alarm-classes-reference/network.md#network-rsvp-neighbor-down) | :material-arrow-up: opening event | dispose |



## Network | RSVP | Neighbor Up
### Symptoms
Routing table changes


### Probable Causes
RSVP successfully established Neighbor with neighbor


### Recommended Actions
No reaction needed


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |
| neighbor | `ip_address` | Neighbor's NSAP or name | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| RSVP \| Neighbor Down](../alarm-classes-reference/network.md#network-rsvp-neighbor-down) | :material-arrow-down: closing event | dispose |



## Network | SONET | Path Status Change




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ no }} |
| state | `str` | Status | {{ yes }} |




## Network | STP | BPDU Guard Recovery




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| STP \| BPDU Guard Violation](../alarm-classes-reference/network.md#network-stp-bpdu-guard-violation) | :material-arrow-down: closing event | dispose |



## Network | STP | BPDU Guard Violation




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| STP \| BPDU Guard Violation](../alarm-classes-reference/network.md#network-stp-bpdu-guard-violation) | :material-arrow-up: opening event | dispose |



## Network | STP | BPDU Root Violation




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| STP \| Root Guard Violation](../alarm-classes-reference/network.md#network-stp-root-guard-violation) | :material-arrow-up: opening event | dispose |



## Network | STP | Inconsistency Update STP




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| port | `interface_name` | Interface | {{ no }} |
| vlan | `int` | vlan | {{ yes }} |
| state | `str` | Status | {{ yes }} |




## Network | STP | Root Changed
### Symptoms
Unexpected MAC address table cleanups, short-time traffic disruptions




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |
| vlan | `int` | VLAN ID | {{ no }} |
| instance | `int` | MST instance | {{ no }} |




## Network | STP | Root Guard Recovery




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| STP \| Root Guard Violation](../alarm-classes-reference/network.md#network-stp-root-guard-violation) | :material-arrow-down: closing event | dispose |



## Network | STP | STP Loop Cleared




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| STP \| STP Loop Detected](../alarm-classes-reference/network.md#network-stp-stp-loop-detected) | :material-arrow-down: closing event | dispose |



## Network | STP | STP Loop Detected




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| STP \| STP Loop Detected](../alarm-classes-reference/network.md#network-stp-stp-loop-detected) | :material-arrow-up: opening event | dispose |



## Network | STP | STP Port Role Changed
### Symptoms
possible start of spanning tree rebuilding or interface oper status change




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |
| role | `str` | Port Role | {{ yes }} |
| vlan | `int` | VLAN ID | {{ no }} |
| instance | `int` | MST instance | {{ no }} |




## Network | STP | STP Port State Changed
### Symptoms
possible start of spanning tree rebuilding or interface oper status change




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |
| state | `str` | Port State | {{ yes }} |
| vlan | `int` | VLAN ID | {{ no }} |
| instance | `int` | MST instance | {{ no }} |




## Network | STP | STP Vlan Loop Cleared




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |
| vlan | `int` | vlan | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| STP \| STP Vlan Loop Detected](../alarm-classes-reference/network.md#network-stp-stp-vlan-loop-detected) | :material-arrow-down: closing event | dispose |



## Network | STP | STP Vlan Loop Detected




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |
| vlan | `int` | vlan | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| STP \| STP Vlan Loop Detected](../alarm-classes-reference/network.md#network-stp-stp-vlan-loop-detected) | :material-arrow-up: opening event | dispose |



## Network | STP | STP instances exceeded




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| limit | `int` | Platform limit | {{ no }} |




## Network | STP | Topology Changed
### Symptoms
Unexpected MAC address table cleanups, short-time traffic disruptions




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |
| vlan | `int` | VLAN ID | {{ no }} |
| instance | `int` | MST instance | {{ no }} |




## Network | Storm Control | Broadcast Storm Cleared




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Storm Control \| Broadcast Storm Detected](../alarm-classes-reference/network.md#network-storm-control-broadcast-storm-detected) | :material-arrow-down: closing event | dispose |



## Network | Storm Control | Broadcast Storm Detected




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Storm Control \| Broadcast Storm Detected](../alarm-classes-reference/network.md#network-storm-control-broadcast-storm-detected) | :material-arrow-up: opening event | dispose |



## Network | Storm Control | Multicast Storm Cleared




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Storm Control \| Multicast Storm Detected](../alarm-classes-reference/network.md#network-storm-control-multicast-storm-detected) | :material-arrow-down: closing event | dispose |



## Network | Storm Control | Multicast Storm Detected




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Storm Control \| Multicast Storm Detected](../alarm-classes-reference/network.md#network-storm-control-multicast-storm-detected) | :material-arrow-up: opening event | dispose |



## Network | Storm Control | Storm Cleared




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Storm Control \| Storm Detected](../alarm-classes-reference/network.md#network-storm-control-storm-detected) | :material-arrow-down: closing event | dispose |



## Network | Storm Control | Storm Detected




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Storm Control \| Storm Detected](../alarm-classes-reference/network.md#network-storm-control-storm-detected) | :material-arrow-up: opening event | dispose |



## Network | Storm Control | Unicast Storm Cleared




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Storm Control \| Unicast Storm Detected](../alarm-classes-reference/network.md#network-storm-control-unicast-storm-detected) | :material-arrow-down: closing event | dispose |



## Network | Storm Control | Unicast Storm Detected



### Recommended Actions
Enable DLF (destination lookup failure) filter


### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| Storm Control \| Unicast Storm Detected](../alarm-classes-reference/network.md#network-storm-control-unicast-storm-detected) | :material-arrow-up: opening event | dispose |



## Network | UDLD | UDLD Protocol Error Detected




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| UDLD \| UDLD Protocol Error Detected](../alarm-classes-reference/network.md#network-udld-udld-protocol-error-detected) | :material-arrow-up: opening event | dispose |



## Network | UDLD | UDLD Protocol Recovery




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |


### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
| [Network \| UDLD \| UDLD Protocol Error Detected](../alarm-classes-reference/network.md#network-udld-udld-protocol-error-detected) | :material-arrow-down: closing event | dispose |



## Network | VLAN | Trunk Port Status Changed




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| status | `str` | Port status | {{ yes }} |
| interface | `interface_name` | Interface | {{ yes }} |




## Network | VLAN | VLAN Created




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| vlan | `int` | VLAN ID | {{ yes }} |
| name | `str` | VLAN Name | {{ no }} |




## Network | VLAN | VLAN Deleted




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| vlan | `int` | VLAN ID | {{ yes }} |
| name | `str` | VLAN Name | {{ no }} |




## Network | VRRP | New Master




### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
| interface | `interface_name` | Interface | {{ yes }} |
| ip | `ip_address` | IP address | {{ yes }} |



