.. _event-class-network-is-is-adjacency-down:

================================
Network | IS-IS | Adjacency Down
================================
.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

IS-IS adjacency down

Symptoms
--------
Routing table changes and possible lost of connectivity

Probable Causes
---------------
ISIS successfully established adjacency with neighbor

Recommended Actions
-------------------
Check links and local and neighbor's router configuration

Variables
----------
==================== ==================================================
Name                 Description
==================== ==================================================
neighbor             Neighbor's NSAP or name
interface            Interface
level                Level
reason               Adjacency lost reason
==================== ==================================================

Alarms
------
================= ======================================================================
Opening Event for :ref:`alarm-class-network-is-is-adjacency-down`
================= ======================================================================
