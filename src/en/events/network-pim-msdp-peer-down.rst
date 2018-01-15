.. _event-class-network-pim-msdp-peer-down:

==============================
Network | PIM | MSDP Peer Down
==============================
.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

MSDP peer down

Symptoms
--------
Multicast flows lost

Probable Causes
---------------
MSDP protocol configuration problem or link failure

Recommended Actions
-------------------
Check links and local and neighbor's router configuration

Variables
----------
==================== ==================================================
Name                 Description
==================== ==================================================
peer                 Peer's IP
vrf                  VRF
reason               Reason
==================== ==================================================

Alarms
------
================= ======================================================================
Opening Event for :ref:`alarm-class-network-pim-msdp-peer-down`
================= ======================================================================
