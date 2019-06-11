.. _alarm-class-network-lbd-vlan-loop-detected:

==================================
Network | LBD | Vlan Loop Detected
==================================
.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Symptoms
--------
Lost traffic on specific vlan

Probable Causes
---------------
.. todo::
    Describe Network | LBD | Vlan Loop Detected probable causes

Recommended Actions
-------------------
Check topology or use STP to avoid loops

Variables
----------
==================== ==================================================
Name                 Description
==================== ==================================================
interface            interface
vlan                 Vlan
description          Interface description
vlan_name            Vlan name
vlan_description     Vlan description
vlan_vc_domain       VC domain
==================== ==================================================

Events
------
============= ======================================================================
Closing Event :ref:`event-class-network-lbd-vlan-loop-cleared`
Opening Event :ref:`event-class-network-lbd-vlan-loop-detected`
============= ======================================================================
