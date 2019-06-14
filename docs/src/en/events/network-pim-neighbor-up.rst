.. _event-class-network-pim-neighbor-up:

===========================
Network | PIM | Neighbor Up
===========================
.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

PIM Neighbor up

Symptoms
--------
Multicast flows send successfully

Probable Causes
---------------
PIM successfully established connect with neighbor

Recommended Actions
-------------------
No reaction needed

Variables
----------
==================== ==================================================
Name                 Description
==================== ==================================================
interface            Interface
neighbor             Neighbor's IP
vrf                  VRF
==================== ==================================================

Alarms
------
================= ======================================================================
Closing Event for :ref:`alarm-class-network-pim-neighbor-down`
================= ======================================================================
