.. _event-class-noc-unknown-event-source:

==========================
NOC | Unknown Event Source
==========================
.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Unknown Event Source

Symptoms
--------
Events from particular device are ignored by Fault Management

Probable Causes
---------------
Event's source address does not belong to any Managed Object's trap_source

Recommended Actions
-------------------
Add appropriative Managed Object or fix trap_source

Variables
----------
==================== ==================================================
Name                 Description
==================== ==================================================
ip                   Event SRC IP
collector_ip         Collector's IP address
collector_port       Collector's port
activator            Activator pool
==================== ==================================================
