# Network


## Network | BFD | Session Down




### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| interface | BFD interface |  |
| peer | BFD Peer |  |
| description | Interface description |  |



## Network | BGP | Peer Down




### Variables
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



## Network | BGP | Prefix Limit Exceeded




### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| peer | BGP Peer |  |
| vrf | VRF |  |
| as | BGP Peer AS |  |



## Network | CEF | Resource Failure




### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| peer | BFD Peer |  |
| reason | Reason failed |  |



## Network | DHCP | Untrusted Server




### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| ip | Source IP |  |
| interface | Source interface |  |



## Network | DNS | Bad Query




### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| ip | Source IP |  |



## Network | DOCSIS | BPI Unautorized


### Probable Causes
An unauthorized cable modem has been deleted to enforce BPI authorization for the specified cable modem. The specified cable modem was not performing BPI negotiation.


### Recommended Actions
Check the modem interface configuration for privacy mandatory, or check for errors in the TFTP configuration file.


### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| mac | Cable Modem MAC |  |
| sid | Cable Modem SID |  |
| interface | Cable interface |  |



## Network | DOCSIS | Bad Timing Offset


### Probable Causes
The cable modem is not using the correct starting offset during initial ranging, causing a zero, negative timing offset to be recorded by the CMTS for this modem. The CMTS internal algorithms that rely on the timing offset parameter will not analyze any modems that do not use the correct starting offset. The modems may not be able to function, depending on their physical location on the cable plant.


### Recommended Actions
Locate the cable modem based on the MAC address and report the initial timing offset problem to the cable modem vendor.


### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| mac | Cable Modem MAC |  |
| sid | Cable Modem SID |  |
| offset | Time offset |  |



## Network | DOCSIS | Invalid CoS


### Probable Causes
The registration of the specified modem has failed because of an invalid or unsupported CoS setting.


### Recommended Actions
Ensure that the CoS fields in the configuration file are set correctly.


### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| mac | Cable Modem MAC |  |
| sid | Cable Modem SID |  |
| interface | Cable interface |  |



## Network | DOCSIS | Invalid DOCSIS Message


### Probable Causes
A cable modem that is not DOCSIS-compliant has attempted to send an invalid DOCSIS message.


### Recommended Actions
Locate the cable modem that sent this message and replace it with DOCSIS-compliant modem.


### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| interface | Cable interface |  |
| mac | Cable Modem MAC |  |
| sid | Cable Modem SID |  |



## Network | DOCSIS | Invalid QoS


### Probable Causes
The registration of the specified modem has failed because of an invalid or unsupported QoS setting.


### Recommended Actions
Ensure that the QoS fields in the configuration file are set correctly.


### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| mac | Cable Modem MAC |  |
| sid | Cable Modem SID |  |
| interface | Cable interface |  |



## Network | DOCSIS | Invalid Shared Secret


### Probable Causes
The registration of this modem has failed because of an invalid MIC string.


### Recommended Actions
Ensure that the shared secret that is in the configuration file is the same as the shared secret that is configured in the cable modem.


### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| mac | Cable Modem MAC |  |
| sid | Cable Modem SID |  |
| interface | Cable interface |  |



## Network | DOCSIS | Max CPE Reached


### Probable Causes
The maximum number of devices that can be attached to the cable modem has been exceeded. Therefore, the device with the specified IP address will not be added to the modem with the specified SID.


### Recommended Actions
Locate the specified device and place the device on a different cable modem with another SID.


### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| mac | CPE MAC |  |
| ip | CPE IP |  |
| modem_mac | Cable Modem MAC |  |
| sid | Cable Modem SID |  |
| interface | Cable interface |  |



## Network | DOCSIS | Maximum Capacity Reached


### Probable Causes
The currently reserved capacity on the upstream channel already exceeds its virtual reservation capacity, based on the configured subscription level limit. Increasing the subscription level limit on the current upstream channel will place you at risk of being unable to guarantee the individual reserved rates for modems since this upstream channel is already oversubscribed.


### Recommended Actions
Load-balance the modems that are requesting the reserved upstream rate on another upstream channel.


### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| interface | Cable interface |  |
| upstream | Upstream |  |
| cur_bps | Current bps reservation |  |
| res_bps | Reserved bps |  |



## Network | DOCSIS | Maximum SIDs


### Probable Causes
The maximum number of SIDs has been allocated to the specified line card.


### Recommended Actions
Assign the cable modem to another line card.


### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| interface | Cable interface |  |



## Network | EIGRP | Neighbor Down

### Symptoms
Routing table changes and possible lost of connectivity


### Probable Causes
Link failure or protocol misconfiguration


### Recommended Actions
Check links and local and neighbor router configuration


### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| as | EIGRP autonomus system |  |
| interface | Interface |  |
| neighbor | Neighbor's Router ID |  |
| reason | Adjacency lost reason |  |
| description | Interface description |  |



## Network | IMPB | Unauthenticated IP-MAC

### Symptoms
Discard user connection attempts



### Recommended Actions
Check user IP and MAC, check IMPB entry, check topology


### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| ip | User IP |  |
| mac | User MAC |  |
| interface | Affected interface |  |
| description | Interface description |  |



## Network | IP | ARP Moved




### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| interface | BFD interface |  |
| ip | IP |  |
| from_mac | From MAC |  |
| to_mac | To MAC |  |



## Network | IP | Address Conflict




### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| ip | Conflicting IP |  |
| mac | MAC |  |
| interface | Interface |  |



## Network | IP | IP Flap




### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| ip | Flapped IP |  |
| from_interface | From interface |  |
| to_interface | To interface |  |
| mac | MAC |  |



## Network | IS-IS | Adjacency Down

### Symptoms
Routing table changes and possible lost of connectivity


### Probable Causes
Link failure or protocol misconfiguration


### Recommended Actions
Check links and local and neighbor router configuration


### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| interface | Interface |  |
| neighbor | Neighbor's NSAP or name |  |
| level | Level |  |
| reason | Adjacency lost reason |  |



## Network | LBD | Loop Detected



### Recommended Actions
Check hardware link and topology


### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| interface | interface |  |
| description | Interface description |  |



## Network | LBD | Vlan Loop Detected

### Symptoms
Lost traffic on specific vlan



### Recommended Actions
Check topology or use STP to avoid loops


### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| interface | interface |  |
| vlan | Vlan |  |
| description | Interface description |  |
| vlan_name | Vlan name |  |
| vlan_description | Vlan description |  |
| vlan_l2_domain | L2 domain |  |



## Network | Link | DOM | Alarm: Out of Threshold

### Symptoms
Connection lost




### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| interface | Physical port |  |
| threshold | Threshold type |  |
| sensor | Measured name |  |
| ovalue | Operating value |  |
| tvalue | Threshold value |  |
| description | Interface description |  |



## Network | Link | DOM | Warning: Out of Threshold

### Symptoms
Connection lost




### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| interface | Physical port |  |
| threshold | Threshold type |  |
| sensor | Measured name |  |
| ovalue | Operating value |  |
| tvalue | Threshold value |  |
| description | Interface description |  |



## Network | Link | Duplex Mismatch




### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| interface | interface name |  |
| description | Interface description |  |



## Network | Link | Err-Disable




### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| interface | interface name |  |
| reason | err-disable reason |  |
| description | Interface description |  |



## Network | Link | Half-Duplex




### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| interface | interface name |  |
| description | Interface description |  |



## Network | Link | Link Down

### Symptoms
Connection lost


### Probable Causes
Administrative action, cable damage, hardware or software error either from this or from another side


### Recommended Actions
Check configuration, both sides of links and hardware


### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| interface | interface name |  |
| description | Interface description |  |
| link | Link ID |  |



## Network | MAC | Duplicate MAC




### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| mac | MAC Address |  |
| one_interface | First interface |  |
| two_interface | Second interface |  |
| one_description | Interface description |  |
| two_description | Interface description |  |



## Network | MAC | Invalid MAC




### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| mac | MAC Address |  |
| interface | Affected interface |  |
| vlan | Affected vlan |  |
| description | Interface description |  |



## Network | MAC | Link MAC Exceed




### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| mac_limit | MAC Address Limit |  |
| utilization | Utilization |  |
| interface | Interface |  |



## Network | MAC | MAC Flap


### Probable Causes
The system found the specified host moving between the specified ports.


### Recommended Actions
Examine the network for possible loops.


### Variables
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



## Network | MAC | MAC Flood




### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| mac | MAC Address |  |
| vlan | VLAN |  |
| interface | Interface |  |
| vlan_name | Vlan name |  |
| vlan_description | Vlan description |  |
| vlan_l2_domain | L2 domain |  |



## Network | MPLS | LDP Neighbor Down




### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| neighbor | LDP Neighbor |  |
| state | State |  |
| reason | Reason |  |



## Network | MPLS | LDP Session Down




### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| interface | interface name |  |
| state | State |  |
| reason | Reason |  |



## Network | MPLS | LSP Down




### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| name | LSP name |  |
| state | State |  |
| reason | Reason |  |



## Network | MPLS | Path Down




### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| name | Path name |  |
| reason | Reason |  |



## Network | MPLS | TDP Neighbor Down




### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| neighbor | TDP Neighbor |  |
| reason | Reason |  |



## Network | MSDP | Peer Down



### Recommended Actions
Check msdp peer aviability, check msdp peer configuration changes


### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| peer | Peer's IP |  |
| vrf | VRF |  |
| reason | Reason |  |



## Network | Monitor | CRC Error Detected




### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| interface | interface |  |
| description | Interface description |  |



## Network | OSPF | Neighbor Down

### Symptoms
Routing table changes and possible lost of connectivity


### Probable Causes
Link failure or protocol misconfiguration


### Recommended Actions
Check links and local and neighbor router configuration


### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| area | OSPF area |  |
| interface | Interface |  |
| neighbor | Neighbor's Router ID |  |
| reason | Adjacency lost reason |  |
| vrf | VRF |  |
| description | Interface description |  |



## Network | PIM | DR Change

### Symptoms
Some multicast flows lost


### Probable Causes
Link failure or protocol misconfiguration


### Recommended Actions
Check links and local and neighbor router configuration


### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| interface | Interface |  |
| from_dr | From DR |  |
| to_dr | To DR |  |
| vrf | VRF |  |



## Network | PIM | Invalid RP


### Probable Causes
A PIM router received a register message from another PIM router that identifies itself as the rendezvous point. If the router is not configured for another rendezvous point, it will not accept the register message.


### Recommended Actions
Configure all leaf routers (first-hop routers to multicast sources) with the IP address of the valid rendezvous point.


### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| pim_router | PIM router IP |  |
| invalid_rp | Invalid RP IP |  |



## Network | PIM | MSDP Peer Down

### Symptoms
Multicast flows lost


### Probable Causes
Link failure or protocol misconfiguration


### Recommended Actions
Check links and local and neighbor router configuration


### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| peer | Peer's IP |  |
| vrf | VRF |  |
| reason | Reason |  |



## Network | PIM | Neighbor Down

### Symptoms
Multicast flows lost


### Probable Causes
Link failure or protocol misconfiguration


### Recommended Actions
Check links and local and neighbor router configuration


### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| interface | Interface |  |
| neighbor | Neighbor's IP |  |
| vrf | VRF |  |
| reason | Reason |  |
| description | Interface description |  |



## Network | Port Security | Port Security Violation




### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| interface | Interface |  |
| mac | MAC Address |  |
| description | Interface description |  |



## Network | Port | Loss of Signal

### Symptoms
Connection lost


### Probable Causes
Administrative action, cable damage, hardware or software error either from this or from another side


### Recommended Actions
Check configuration, both sides of links and hardware


### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| interface | interface name |  |
| description | Interface description |  |
| slot | Slot name |  |
| catrd | Card name |  |



## Network | RSVP | Neighbor Down

### Symptoms
Routing table changes and possible lost of connectivity


### Probable Causes
Link failure or protocol misconfiguration


### Recommended Actions
Check links and local and neighbor router configuration


### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| interface | Interface |  |
| neighbor | Neighbor's NSAP or name |  |
| reason | Neighbor lost reason |  |



## Network | STP | BPDU Guard Violation




### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| interface | interface |  |
| description | Interface description |  |



## Network | STP | Root Guard Violation




### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| interface | interface |  |
| description | Interface description |  |



## Network | STP | STP Loop Detected




### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| interface | interface |  |
| description | Interface description |  |



## Network | STP | STP Vlan Loop Detected




### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| interface | interface |  |
| vlan | vlan |  |
| description | Interface description |  |
| vlan_name | Vlan name |  |
| vlan_description | Vlan description |  |
| vlan_l2_domain | L2 domain |  |



## Network | Storm Control | Broadcast Storm Detected




### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| interface | interface |  |
| description | Interface description |  |



## Network | Storm Control | Multicast Storm Detected




### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| interface | interface |  |
| description | Interface description |  |



## Network | Storm Control | Storm Detected




### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| interface | interface |  |
| description | Interface description |  |



## Network | Storm Control | Unicast Storm Detected



### Recommended Actions
Enable DLF (destination lookup failure) filter


### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| interface | interface |  |
| description | Interface description |  |



## Network | UDLD | UDLD Protocol Error Detected




### Variables
| Name | Description | Defaults |
| --- | --- | --- |
| interface | interface |  |
| description | Interface description |  |


