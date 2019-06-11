.. _event-class-network-ospf-neighbor-up:

============================
Network | OSPF | Neighbor Up
============================
.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

OSPF neighbor up

Symptoms
--------
Routing table changes

Probable Causes
---------------
An OSPF adjacency was established with the indicated neighboring router. The local router can now exchange information with it.

Recommended Actions
-------------------
No specific actions needed

Variables
----------
==================== ==================================================
Name                 Description
==================== ==================================================
area                 OSPF area
interface            Interface
neighbor             Neighbor's Router ID
reason               Adjacency lost reason
from_state           from state
to_state             to state
vrf                  VRF
==================== ==================================================

Alarms
------
================= ======================================================================
Closing Event for :ref:`alarm-class-network-ospf-neighbor-down`
================= ======================================================================
