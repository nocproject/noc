.. _alarm-class-network-docsis-bpi-unautorized:

==================================
Network | DOCSIS | BPI Unautorized
==================================
.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Symptoms
--------
.. todo::
    Describe Network | DOCSIS | BPI Unautorized symptoms

Probable Causes
---------------
An unauthorized cable modem has been deleted to enforce BPI authorization for the specified cable modem. The specified cable modem was not performing BPI negotiation.

Recommended Actions
-------------------
Check the modem interface configuration for privacy mandatory, or check for errors in the TFTP configuration file.

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
Opening Event :ref:`event-class-network-docsis-bpi-unautorized`
============= ======================================================================
