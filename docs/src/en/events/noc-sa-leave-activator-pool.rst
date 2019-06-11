.. _event-class-noc-sa-leave-activator-pool:

===============================
NOC | SA | Leave Activator Pool
===============================
.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol



Symptoms
--------
SA performance decreased

Probable Causes
---------------
noc-activator process been stopped

Recommended Actions
-------------------
Check appropriative process

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
