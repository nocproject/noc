.. _event-class-network-mac-mac-flap:

========================
Network | MAC | MAC Flap
========================
.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

MAC Flap detected

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
==================== ==================================================

Alarms
------
================= ======================================================================
Opening Event for :ref:`alarm-class-network-mac-mac-flap`
================= ======================================================================
