.. _event-class-network-eigrp-neighbor-up:

=============================
Network | EIGRP | Neighbor Up
=============================
.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

EIGRP neighbor up

Symptoms
--------
Routing table changes

Probable Causes
---------------
An EIGRP adjacency was established with the indicated neighboring router. The local router can now exchange information with it.

Recommended Actions
-------------------
No specific actions needed

Variables
----------
==================== ==================================================
Name                 Description
==================== ==================================================
as                   EIGRP autonomus system
interface            Interface
neighbor             Neighbor's Router ID
reason               Adjacency lost reason
to_state             to state
==================== ==================================================

Alarms
------
================= ======================================================================
Closing Event for :ref:`alarm-class-network-eigrp-neighbor-down`
================= ======================================================================
