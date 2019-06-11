.. _event-class-network-docsis-maximum-capacity-reached:

===========================================
Network | DOCSIS | Maximum Capacity Reached
===========================================
.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Current total reservation exceeds maximum configured reservation

Symptoms
--------
.. todo::
    Describe Network | DOCSIS | Maximum Capacity Reached symptoms

Probable Causes
---------------
The currently reserved capacity on the upstream channel already exceeds its virtual reservation capacity, based on the configured subscription level limit. Increasing the subscription level limit on the current upstream channel will place you at risk of being unable to guarantee the individual reserved rates for modems since this upstream channel is already oversubscribed.

Recommended Actions
-------------------
Load-balance the modems that are requesting the reserved upstream rate on another upstream channel.

Variables
----------
==================== ==================================================
Name                 Description
==================== ==================================================
interface            Cable interface
upstream             Upstream
cur_bps              Current bps reservation
res_bps              Reserved bps
==================== ==================================================

Alarms
------
================= ======================================================================
Opening Event for :ref:`alarm-class-network-docsis-maximum-capacity-reached`
================= ======================================================================
