.. _alarm-class-network-bgp-peer-down:

=========================
Network | BGP | Peer Down
=========================
.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Symptoms
--------
.. todo::
    Describe Network | BGP | Peer Down symptoms

Probable Causes
---------------
.. todo::
    Describe Network | BGP | Peer Down probable causes

Recommended Actions
-------------------
.. todo::
    Describe Network | BGP | Peer Down recommended actions

Variables
----------
==================== ==================================================
Name                 Description
==================== ==================================================
peer                 BGP Peer
vrf                  VRF
reason               Reason
as                   BGP Peer AS
local_as             Local AS
description          BGP Peer Description
import_filter        BGP Import Filter
export_filter        BGP Export Filter
==================== ==================================================

Events
------
============= ======================================================================
Opening Event :ref:`event-class-network-bgp-backward-transition`
Closing Event :ref:`event-class-network-bgp-established`
Opening Event :ref:`event-class-network-bgp-peer-down`
Closing Event :ref:`event-class-network-bgp-peer-state-changed`
Opening Event :ref:`event-class-network-bgp-peer-state-changed`
============= ======================================================================
