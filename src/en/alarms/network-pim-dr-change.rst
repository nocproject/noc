.. _alarm-class-network-pim-dr-change:

=========================
Network | PIM | DR Change
=========================
.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Symptoms
--------
Some multicast flows lost

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
from_dr              From DR
to_dr                To DR
vrf                  VRF
==================== ==================================================

Events
------
============= ======================================================================
Opening Event :ref:`event-class-network-pim-dr-change`
============= ======================================================================
