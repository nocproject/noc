.. _alarm-class-network-link-link-down:

==========================
Network | Link | Link Down
==========================
.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Symptoms
--------
Connection lost

Probable Causes
---------------
Administrative action, cable damage, hardware or software error either from this or from another side

Recommended Actions
-------------------
Check configuration, both sides of links and hardware

Variables
----------
==================== ==================================================
Name                 Description
==================== ==================================================
interface            interface name
description          Interface description
link                 Link ID
==================== ==================================================

Root Cause Analysis
-------------------
============== ======================================================================
Root Cause for :ref:`alarm-class-network-bfd-session-down`
Root Cause for :ref:`alarm-class-network-eigrp-neighbor-down`
Root Cause for :ref:`alarm-class-network-is-is-adjacency-down`
Root Cause for :ref:`alarm-class-network-link-link-down`
Root Cause for :ref:`alarm-class-network-ospf-neighbor-down`
Root Cause for :ref:`alarm-class-network-pim-neighbor-down`
Consequence of :ref:`alarm-class-chassis-hardware-hardware-port-error`
Consequence of :ref:`alarm-class-chassis-linecard-lc-down`
Consequence of :ref:`alarm-class-network-lbd-loop-detected`
Consequence of :ref:`alarm-class-network-link-dom-alarm:-out-of-threshold`
Consequence of :ref:`alarm-class-network-link-err-disable`
Consequence of :ref:`alarm-class-network-link-link-down`
Consequence of :ref:`alarm-class-network-stp-stp-loop-detected`
============== ======================================================================

Events
------
============= ======================================================================
Opening Event :ref:`event-class-network-link-link-down`
Closing Event :ref:`event-class-network-link-link-up`
============= ======================================================================
