**************************
Virtual Circuit Management
**************************
Overview
========
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

Forms
=====
Virtual Circuits
----------------
Importing existing VCs
^^^^^^^^^^^^^^^^^^^^^^

* Press "Import VLANs from switch" button (upper right corner).
* Select VC Domain to put collected VLANs and switch from which to pull VLANs. Switch must be set up as Managed Object (see Service Activation manual).

Permissions
^^^^^^^^^^^
======= ========================================
add     vc | VC | Can add VC
change  vc | VC | Can change VC
delete  vc | VC | Can delete VC
======= ========================================

Setup
=====
VC Domains
----------
Permissions
^^^^^^^^^^^
======= ========================================
add     vc | VC Domain | Can add VC Domain
change  vc | VC Domain | Can change VC Domain
delete  vc | VC Domain | Can delete VC Domain
======= ========================================

Permissions
^^^^^^^^^^^
======= ========================================
preview ANY
======= ========================================

