.. _alarm-class-network-pim-neighbor-down:

=============================
Network | PIM | Neighbor Down
=============================
.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Symptoms
--------
Multicast flows lost

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
neighbor             Neighbor's IP
vrf                  VRF
reason               Reason
description          Interface description
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
Opening Event :ref:`event-class-network-pim-neighbor-down`
Closing Event :ref:`event-class-network-pim-neighbor-up`
============= ======================================================================
