.. _event-class-network-pim-dr-change:

=========================
Network | PIM | DR Change
=========================
.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Designated Router Change

Symptoms
--------
Some multicast flows lost

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
from_dr              From DR
to_dr                To DR
vrf                  VRF
==================== ==================================================

Alarms
------
================= ======================================================================
Opening Event for :ref:`alarm-class-network-pim-dr-change`
================= ======================================================================
