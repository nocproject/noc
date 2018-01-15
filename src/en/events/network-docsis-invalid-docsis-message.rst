.. _event-class-network-docsis-invalid-docsis-message:

=========================================
Network | DOCSIS | Invalid DOCSIS Message
=========================================
.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Invalid DOCSIS Message received from a Cable Modem

Symptoms
--------
.. todo::
    Describe Network | DOCSIS | Invalid DOCSIS Message symptoms

Probable Causes
---------------
A cable modem that is not DOCSIS-compliant has attempted to send an invalid DOCSIS message.

Recommended Actions
-------------------
Locate the cable modem that sent this message and replace it with DOCSIS-compliant modem.

Variables
----------
==================== ==================================================
Name                 Description
==================== ==================================================
interface            Cable interface
mac                  Cable Modem MAC
sid                  Cable Modem SID
==================== ==================================================

Alarms
------
================= ======================================================================
Opening Event for :ref:`alarm-class-network-docsis-invalid-docsis-message`
================= ======================================================================
