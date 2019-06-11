.. _alarm-class-network-mac-mac-flap:

========================
Network | MAC | MAC Flap
========================
.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Symptoms
--------
.. todo::
    Describe Network | MAC | MAC Flap symptoms

Probable Causes
---------------
The system found the specified host moving between the specified ports.

Recommended Actions
-------------------
Examine the network for possible loops.

Variables
----------
==================== ==================================================
Name                 Description
==================== ==================================================
mac                  MAC Address
vlan                 VLAN
from_interface       From interface
to_interface         To interface
from_description     Interface description
to_description       Interface description
vlan_name            Vlan name
vlan_description     Vlan description
vlan_vc_domain       VC domain
==================== ==================================================

Events
------
============= ======================================================================
Opening Event :ref:`event-class-network-mac-mac-flap`
============= ======================================================================
