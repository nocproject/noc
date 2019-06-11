.. _alarm-class-network-pim-invalid-rp:

==========================
Network | PIM | Invalid RP
==========================
.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Symptoms
--------
.. todo::
    Describe Network | PIM | Invalid RP symptoms

Probable Causes
---------------
A PIM router received a register message from another PIM router that identifies itself as the rendezvous point. If the router is not configured for another rendezvous point, it will not accept the register message.

Recommended Actions
-------------------
Configure all leaf routers (first-hop routers to multicast sources) with the IP address of the valid rendezvous point.

Variables
----------
==================== ==================================================
Name                 Description
==================== ==================================================
pim_router           PIM router IP
invalid_rp           Invalid RP IP
==================== ==================================================

Events
------
============= ======================================================================
Opening Event :ref:`event-class-network-pim-invalid-rp`
============= ======================================================================
