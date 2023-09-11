# Allocation Group

Allocation Group is the way to apply additional uniqueness limitation
for various logical resources allocation:

- VLAN
- IP Address
- IP Prefixes

Allocation Groups are used to avoid possible conflicts and intersections
when connecting various parts of the network

# Mobile Network Address Plan

Mobile networks often use 3 VRFs to separate various types of traffic
and imply additional network processing, namely:

- Network Management
- Voice
- Mobile data

Prefixes and address allocation in each VRF performed independentently by
default. So its easy to allocate same prefixes and addresses in
different VRFs. While the address plan independentence is a core concept of VRF,
it can lead to various practical problems:

- Network equipment may not be aware of VRFs at all and cannot reuse
  same addresses or networks for different purposes
  (like Voice and Management for SBCs)
- Possible traffic leaking due to configuration mistakes
- Complicated traffic analysis

Solution is to create common Allocation Group and apply it to all 3 VRFs.
So same network can be allocated only in one VRF, ensuring network uniqueness

# Common VLAN space

Consider several Points-of-Presence (Branch offices, datacenters, etc)
connected by equipment incapable of VLAN tag manipulation. Any VLAN
from one PoP may be extended to another PoP any time. If same VLAN may be
allocated for different purpose at different PoPs there will be problem
when trying to extend any of VLANs, requiring expensive VLAN renumbering
at one PoP.

Solution is to create common Allocation Group and apply it to appropriate
PoP's segments. So same VLAN can be allocated only in one PoP, ensuring
VLAN uniqueness
