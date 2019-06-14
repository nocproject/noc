.. _alarm-class-network-rsvp-neighbor-down:

==============================
Network | RSVP | Neighbor Down
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
interface            Interface
neighbor             Neighbor's NSAP or name
reason               Neighbor lost reason
==================== ==================================================

Events
------
============= ======================================================================
Opening Event :ref:`event-class-network-rsvp-neighbor-down`
Closing Event :ref:`event-class-network-rsvp-neighbor-up`
============= ======================================================================
