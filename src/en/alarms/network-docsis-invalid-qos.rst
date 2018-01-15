.. _alarm-class-network-docsis-invalid-qos:

==============================
Network | DOCSIS | Invalid QoS
==============================
.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Symptoms
--------
.. todo::
    Describe Network | DOCSIS | Invalid QoS symptoms

Probable Causes
---------------
The registration of the specified modem has failed because of an invalid or unsupported QoS setting.

Recommended Actions
-------------------
Ensure that the QoS fields in the configuration file are set correctly.

Variables
----------
==================== ==================================================
Name                 Description
==================== ==================================================
mac                  Cable Modem MAC
sid                  Cable Modem SID
interface            Cable interface
==================== ==================================================

Events
------
============= ======================================================================
Opening Event :ref:`event-class-network-docsis-invalid-qos`
============= ======================================================================
