.. _event-class-network-eigrp-neighbor-down:

===============================
Network | EIGRP | Neighbor Down
===============================
.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

EIGRP adjacency down

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
as                   EIGRP automonus system
interface            Interface
neighbor             Neighbor's Router ID
reason               Adjacency lost reason
to_state             to state
==================== ==================================================

Alarms
------
================= ======================================================================
Opening Event for :ref:`alarm-class-network-eigrp-neighbor-down`
================= ======================================================================
