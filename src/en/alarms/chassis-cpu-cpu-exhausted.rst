.. _alarm-class-chassis-cpu-cpu-exhausted:

=============================
Chassis | CPU | CPU Exhausted
=============================
.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Symptoms
--------
Device not responce, can not establish new connections

Probable Causes
---------------
High CPU utilization

Recommended Actions
-------------------
Lower storm detect threshold, filter waste traffic on connected devices, restrict SNMP Views


Events
------
============= ======================================================================
Opening Event :ref:`event-class-vendor-dlink-dxs-chassis-cpu-safeguard-engine-enters-exhausted-mode`
Closing Event :ref:`event-class-vendor-dlink-dxs-chassis-cpu-safeguard-engine-enters-normal-mode`
============= ======================================================================
