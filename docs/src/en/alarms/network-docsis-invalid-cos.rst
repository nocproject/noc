.. _alarm-class-network-docsis-invalid-cos:

==============================
Network | DOCSIS | Invalid CoS
==============================
.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Symptoms
--------
.. todo::
    Describe Network | DOCSIS | Invalid CoS symptoms

Probable Causes
---------------
The registration of the specified modem has failed because of an invalid or unsupported CoS setting.

Recommended Actions
-------------------
Ensure that the CoS fields in the configuration file are set correctly.

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
Opening Event :ref:`event-class-network-docsis-invalid-cos`
============= ======================================================================
