.. _event-class-security-authentication-snmp-authentication-failure:

=======================================================
Security | Authentication | SNMP Authentication Failure
=======================================================
.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

SNMP authentication failure

Symptoms
--------
NOC, NMS and monitoring systems cannot interact with the box over SNMP protocol

Probable Causes
---------------
SNMP server is misconfigured, community mismatch, misconfigured ACL or brute-force attack in progress

Recommended Actions
-------------------
Check SNMP configuration

Variables
----------
==================== ==================================================
Name                 Description
==================== ==================================================
ip                   Request source address
community            Request SNMP community
==================== ==================================================

Alarms
------
================= ======================================================================
Opening Event for :ref:`alarm-class-noc-managed-object-configuration-errors-misconfigured-snmp`
================= ======================================================================
