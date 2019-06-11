.. _event-class-network-pim-neighbor-down:

=============================
Network | PIM | Neighbor Down
=============================
.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

PIM Neighbor down

Symptoms
--------
Multicast flows lost

Probable Causes
---------------
PIM protocol configuration problem or link failure

Recommended Actions
-------------------
Check links and local and neighbor's router configuration

Variables
----------
==================== ==================================================
Name                 Description
==================== ==================================================
interface            Interface
neighbor             Neighbor's IP
vrf                  VRF
reason               Reason
==================== ==================================================

Alarms
------
================= ======================================================================
Opening Event for :ref:`alarm-class-network-pim-neighbor-down`
================= ======================================================================
