Overview
********
Virtual circuits management. Simple database of allocated VC identifiers of different types.
VCs are separated into VC Domains while remain unique within VC Domain and own kind.

Supported VC Types:
 * 802.1Q VLAN
 * 802.1ad Q-in-Q VLAN stack
 * FrameRelay DLCI
 * MPLS label stack (up to 2 labels)
 * ATM VPI/VCI
 * X.25 logical groups/logical channel
 
Terminology
============
* VC Domain - Administrative entry within all VCs of any given type are unique
* VC - virtual circuit. Combination of one or two L2/L2.5 labels. Common examples: VLANs, VLAN stacks.
