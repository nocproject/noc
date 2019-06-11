.. _event-class-noc-sa-join-activator-pool:

==============================
NOC | SA | Join Activator Pool
==============================
.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol



Symptoms
--------
SA performance increased

Probable Causes
---------------
noc-activator process been launched

Recommended Actions
-------------------
No recommended actions

Variables
----------
==================== ==================================================
Name                 Description
==================== ==================================================
name                 Activator pool name
instance             Activator instance
sessions             Instance's script sessions
min_members          Pool's members lower threshold
min_sessions         Pool's sessions lower threshold
pool_members         Pool's current members
pool_sessions        Pool's current sessions limit
==================== ==================================================

Alarms
------
================= ======================================================================
Closing Event for :ref:`alarm-class-noc-sa-activator-pool-degraded`
Opening Event for :ref:`alarm-class-noc-sa-activator-pool-degraded`
================= ======================================================================
