.. _alarm-class-noc-sa-activator-pool-degraded:

==================================
NOC | SA | Activator Pool Degraded
==================================
.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Symptoms
--------
Cannot run SA tasks. Too many timeout errors

Probable Causes
---------------
noc-activator processes down

Recommended Actions
-------------------
Check noc-activator processes. Check network connectivity

Variables
----------
==================== ==================================================
Name                 Description
==================== ==================================================
name                 Pool Name
==================== ==================================================

Events
------
============= ======================================================================
Closing Event :ref:`event-class-noc-sa-join-activator-pool`
Opening Event :ref:`event-class-noc-sa-join-activator-pool`
Closing Event :ref:`event-class-noc-sa-leave-activator-pool`
Opening Event :ref:`event-class-noc-sa-leave-activator-pool`
============= ======================================================================
