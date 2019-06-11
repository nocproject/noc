.. _alarm-class-network-ospf-neighbor-down:

==============================
Network | OSPF | Neighbor Down
==============================
.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Symptoms
--------
Routing table changes and possible lost of connectivity

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
area                 OSPF area
interface            Interface
neighbor             Neighbor's Router ID
reason               Adjacency lost reason
vrf                  VRF
description          Interface description
==================== ==================================================

Root Cause Analysis
-------------------
============== ======================================================================
Consequence of :ref:`alarm-class-network-link-link-down`
============== ======================================================================

Events
------
============= ======================================================================
Opening Event :ref:`event-class-network-ospf-neighbor-down`
Closing Event :ref:`event-class-network-ospf-neighbor-up`
============= ======================================================================
