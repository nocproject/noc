.. _alarm-class-noc-managed-object-ping-failed:

==================================
NOC | Managed Object | Ping Failed
==================================
.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Symptoms
--------
Cannot execute SA tasks on the object

Probable Causes
---------------
The object is not responding to ICMP echo-requests

Recommended Actions
-------------------
Check object is alive. Check routing to this object. Check firewalls


Root Cause Analysis
-------------------
============== ======================================================================
Consequence of :ref:`alarm-class-chassis-psu-power-failed`
Consequence of :ref:`alarm-class-system-reboot`
============== ======================================================================

Events
------
============= ======================================================================
Opening Event :ref:`event-class-noc-managed-object-ping-failed`
Closing Event :ref:`event-class-noc-managed-object-ping-ok`
============= ======================================================================
