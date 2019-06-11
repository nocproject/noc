.. _alarm-class-network-is-is-adjacency-down:

================================
Network | IS-IS | Adjacency Down
================================
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
interface            Interface
neighbor             Neighbor's NSAP or name
level                Level
reason               Adjacency lost reason
==================== ==================================================

Root Cause Analysis
-------------------
============== ======================================================================
Consequence of :ref:`alarm-class-network-bfd-session-down`
Consequence of :ref:`alarm-class-network-link-link-down`
============== ======================================================================

Events
------
============= ======================================================================
Opening Event :ref:`event-class-network-is-is-adjacency-down`
Closing Event :ref:`event-class-network-is-is-adjacency-up`
============= ======================================================================
