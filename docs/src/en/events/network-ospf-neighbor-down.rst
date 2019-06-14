.. _event-class-network-ospf-neighbor-down:

==============================
Network | OSPF | Neighbor Down
==============================
.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

OSPF adjacency down

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
from_state           from state
to_state             to state
vrf                  VRF
==================== ==================================================

Alarms
------
================= ======================================================================
Opening Event for :ref:`alarm-class-network-ospf-neighbor-down`
================= ======================================================================
