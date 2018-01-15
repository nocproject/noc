.. _alarm-class-network-docsis-invalid-shared-secret:

========================================
Network | DOCSIS | Invalid Shared Secret
========================================
.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Symptoms
--------
.. todo::
    Describe Network | DOCSIS | Invalid Shared Secret symptoms

Probable Causes
---------------
The registration of this modem has failed because of an invalid MIC string.

Recommended Actions
-------------------
Ensure that the shared secret that is in the configuration file is the same as the shared secret that is configured in the cable modem.

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
Opening Event :ref:`event-class-network-docsis-invalid-shared-secret`
============= ======================================================================
