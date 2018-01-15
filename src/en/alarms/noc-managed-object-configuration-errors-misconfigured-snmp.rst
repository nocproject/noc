.. _alarm-class-noc-managed-object-configuration-errors-misconfigured-snmp:

================================================================
NOC | Managed Object | Configuration Errors | Misconfigured SNMP
================================================================
.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Symptoms
--------
NOC cannot interact with the box over SNMP protocol

Probable Causes
---------------
SNMP server is misconfigured, community mismatch or misconfigured ACL

Recommended Actions
-------------------
Check SNMP configuration

Variables
----------
==================== ==================================================
Name                 Description
==================== ==================================================
ip                   Request source
==================== ==================================================

Events
------
============= ======================================================================
Opening Event :ref:`event-class-security-authentication-snmp-authentication-failure`
============= ======================================================================
