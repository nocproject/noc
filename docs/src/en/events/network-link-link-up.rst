.. _event-class-network-link-link-up:

========================
Network | Link | Link Up
========================
.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Link Up

Symptoms
--------
Connection restored

Probable Causes
---------------
Administrative action, cable or hardware replacement

Recommended Actions
-------------------
Check interfaces on both sides for possible errors

Variables
----------
==================== ==================================================
Name                 Description
==================== ==================================================
interface            Affected interface
speed                Link speed
duplex               Duplex mode
==================== ==================================================

Alarms
------
================= ======================================================================
Closing Event for :ref:`alarm-class-network-link-err-disable`
Closing Event for :ref:`alarm-class-network-link-link-down`
Closing Event for :ref:`alarm-class-network-stp-bpdu-guard-violation`
Closing Event for :ref:`alarm-class-network-stp-root-guard-violation`
================= ======================================================================
