.. _event-class-network-docsis-max-cpe-reached:

==================================
Network | DOCSIS | Max CPE Reached
==================================
.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Maximum number of CPE reached

Symptoms
--------
.. todo::
    Describe Network | DOCSIS | Max CPE Reached symptoms

Probable Causes
---------------
The maximum number of devices that can be attached to the cable modem has been exceeded. Therefore, the device with the specified IP address will not be added to the modem with the specified SID.

Recommended Actions
-------------------
Locate the specified device and place the device on a different cable modem with another SID.

Variables
----------
==================== ==================================================
Name                 Description
==================== ==================================================
mac                  CPE MAC
ip                   CPE IP
modem_mac            Cable Modem MAC
sid                  Cable Modem SID
interface            Cable interface
==================== ==================================================

Alarms
------
================= ======================================================================
Opening Event for :ref:`alarm-class-network-docsis-max-cpe-reached`
================= ======================================================================
