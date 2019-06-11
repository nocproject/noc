.. _alarm-class-network-pim-msdp-peer-down:

==============================
Network | PIM | MSDP Peer Down
==============================
.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Symptoms
--------
Multicast flows lost

Probable Causes
---------------
Link failure or protocol misconfiguration

Recommended Actions
-------------------
Check links and local and neighbor router configuration

Variables
----------
==================== ==================================================
Name                 Description
==================== ==================================================
peer                 Peer's IP
vrf                  VRF
reason               Reason
==================== ==================================================

Events
------
============= ======================================================================
Opening Event :ref:`event-class-network-pim-msdp-peer-down`
Closing Event :ref:`event-class-network-pim-msdp-peer-up`
============= ======================================================================
